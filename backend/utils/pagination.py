"""
Generic cursor-based pagination utilities.

Provides reusable cursor-based pagination helpers for SQLModel/SQLAlchemy
queries with stable multi-column ordering.

The pagination strategy is:

    1. Decode the cursor.
    2. Apply a keyset WHERE condition.
    3. Apply deterministic ordering.
    4. Fetch limit + 1 records.
    5. Use the extra record to determine has_more.
    6. Generate a cursor from the last returned record.

With appropriate database indexes, keyset pagination provides efficient
pagination without the large OFFSET cost associated with traditional
offset-based pagination.
"""

import base64
import binascii
import uuid
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import Select, and_, func, or_
from sqlalchemy import select as sa_select
from sqlmodel import Session

MAX_PAGINATION_LIMIT = 100


def encode_cursor(fields: dict[str, Any]) -> str:
    """
    Encode pagination cursor fields into a URL-safe Base64 string.

    Supported values:
        - datetime
        - UUID
        - int
        - float
        - str

    Example:
        cursor = encode_cursor(
            {
                "created_at": datetime.now(),
                "id": uuid.uuid4(),
            }
        )
    """
    parts: list[str] = []

    for key, value in fields.items():
        if isinstance(value, datetime):
            serialized = f"dt:{value.isoformat()}"

        elif isinstance(value, uuid.UUID):
            serialized = f"uuid:{value}"

        elif isinstance(value, (int, float)):
            serialized = f"num:{value}"

        elif isinstance(value, str):
            serialized = f"str:{value}"

        else:
            raise ValueError(
                f"Unsupported cursor field type for '{key}': {type(value).__name__}"
            )

        parts.append(f"{key}={serialized}")

    cursor_string = "&".join(parts)

    return base64.urlsafe_b64encode(cursor_string.encode("utf-8")).decode("ascii")


def decode_cursor(cursor: str) -> dict[str, Any]:
    """
    Decode a URL-safe Base64 cursor.

    Raises:
        ValueError:
            If the cursor is malformed or contains an unsupported type.
    """
    try:
        decoded = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")

        if not decoded:
            raise ValueError("Cursor is empty")

        fields: dict[str, Any] = {}

        for part in decoded.split("&"):
            if not part:
                continue

            if "=" not in part:
                raise ValueError("Invalid cursor field")

            key, value = part.split("=", 1)

            if not key:
                raise ValueError("Cursor field name cannot be empty")

            if ":" not in value:
                raise ValueError(f"Invalid cursor value for field '{key}'")

            type_prefix, data = value.split(":", 1)

            if type_prefix == "dt":
                fields[key] = datetime.fromisoformat(data)

            elif type_prefix == "uuid":
                fields[key] = uuid.UUID(data)

            elif type_prefix == "num":
                fields[key] = int(data) if "." not in data else float(data)

            elif type_prefix == "str":
                fields[key] = data

            else:
                raise ValueError(f"Unsupported cursor type: {type_prefix}")

        if not fields:
            raise ValueError("Cursor contains no fields")

        return fields

    except (
        ValueError,
        UnicodeDecodeError,
        UnicodeEncodeError,
        binascii.Error,
    ) as exc:
        raise ValueError(f"Invalid cursor format: {exc}") from exc


T = TypeVar("T")


class CursorPaginator:
    """
    Generic keyset/cursor-based paginator.

    Example:

        paginator = CursorPaginator(
            cursor=cursor,
            limit=20,
            order_fields=["created_at", "id"],
            order_direction="desc",
        )

        query = select(Booking).where(
            Booking.user_id == user_id
        )

        query = paginator.apply_cursor_filter(
            query,
            Booking,
        )

        query = paginator.apply_ordering(
            query,
            Booking,
        )

        query = paginator.apply_limit(query)

        items = session.exec(query).all()

        items, next_cursor, has_more = paginator.build_result(
            items,
            lambda booking: {
                "created_at": booking.created_at,
                "id": booking.id,
            },
        )
    """

    def __init__(
        self,
        cursor: str | None,
        limit: int,
        order_fields: list[str],
        order_direction: str = "desc",
    ):
        if limit < 1:
            raise ValueError("Pagination limit must be at least 1")

        if not order_fields:
            raise ValueError("At least one ordering field is required")

        if order_direction not in {"asc", "desc"}:
            raise ValueError("order_direction must be either 'asc' or 'desc'")

        self.cursor = cursor
        self.limit = min(limit, MAX_PAGINATION_LIMIT)
        self.order_fields = order_fields
        self.order_direction = order_direction

        self._cursor_values: dict[str, Any] | None = None

        if cursor:
            self._cursor_values = decode_cursor(cursor)

    def apply_cursor_filter(
        self,
        query: Select,
        model: type,
    ) -> Select:
        """
        Apply the keyset pagination WHERE condition.

        For DESC ordering with:

            order_fields = ["created_at", "id"]

        the condition becomes conceptually:

            created_at < cursor_created_at
            OR (
                created_at = cursor_created_at
                AND id < cursor_id
            )

        For ASC ordering, the comparisons use > instead.
        """
        if not self._cursor_values:
            return query

        conditions = []

        for index, field in enumerate(self.order_fields):
            if field not in self._cursor_values:
                raise ValueError(f"Cursor is missing ordering field: {field}")

            cursor_value = self._cursor_values[field]
            column = getattr(model, field)

            comparison = (
                column < cursor_value
                if self.order_direction == "desc"
                else column > cursor_value
            )

            if index == 0:
                conditions.append(comparison)
                continue

            previous_conditions = []

            for previous_field in self.order_fields[:index]:
                if previous_field not in self._cursor_values:
                    raise ValueError(
                        f"Cursor is missing ordering field: {previous_field}"
                    )

                previous_column = getattr(
                    model,
                    previous_field,
                )

                previous_conditions.append(
                    previous_column == self._cursor_values[previous_field]
                )

            previous_conditions.append(comparison)

            conditions.append(and_(*previous_conditions))

        if conditions:
            query = query.where(or_(*conditions))

        return query

    def apply_ordering(
        self,
        query: Select,
        model: type,
    ) -> Select:
        """
        Apply deterministic ORDER BY clauses.
        """
        order_clauses = []

        for field in self.order_fields:
            column = getattr(model, field)

            if self.order_direction == "desc":
                order_clauses.append(column.desc())
            else:
                order_clauses.append(column.asc())

        return query.order_by(*order_clauses)

    def apply_limit(
        self,
        query: Select,
    ) -> Select:
        """
        Fetch one extra row so we can determine whether another page exists.
        """
        return query.limit(self.limit + 1)

    def build_result(
        self,
        items: Sequence[T],
        cursor_field_extractor: Callable[
            [T],
            dict[str, Any],
        ],
    ) -> tuple[list[T], str | None, bool]:
        """
        Trim the extra row and generate the next cursor.

        Returns:
            (
                items,
                next_cursor,
                has_more,
            )
        """
        items_list = list(items)

        has_more = len(items_list) > self.limit

        if has_more:
            items_list = items_list[: self.limit]

        next_cursor = None

        if has_more and items_list:
            last_item = items_list[-1]

            cursor_fields = cursor_field_extractor(last_item)

            next_cursor = encode_cursor(cursor_fields)

        return (
            items_list,
            next_cursor,
            has_more,
        )


def get_total_count(
    session: Session,
    query: Select,
) -> int:
    """
    Calculate the total number of matching rows.

    This should be used sparingly because COUNT(*) can be expensive
    on large datasets.
    """
    count_query = sa_select(func.count()).select_from(query.subquery())

    result = session.execute(count_query)

    return result.scalar() or 0
