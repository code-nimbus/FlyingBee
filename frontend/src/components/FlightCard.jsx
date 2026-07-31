export default function FlightCard({ flight }) {
    return (
        <div
            style={{
                border: "1px solid #ddd",
                borderRadius: 10,
                padding: 20,
                marginBottom: 20,
            }}
        >
            <h3>{flight.airline}</h3>

            <p>
                <strong>Flight:</strong> {flight.flight_number}
            </p>

            <p>
                {flight.origin} ➜ {flight.destination}
            </p>

            <p>
                Departure:
                {" "}
                {new Date(flight.departure_at).toLocaleString()}
            </p>

            <p>
                Duration:
                {" "}
                {flight.duration}
                {" "}minutes
            </p>

            <p>
                Stops:
                {" "}
                {flight.transfers}
            </p>

            <h2>${flight.price}</h2>

            <a
                href={`https://www.travelpayouts.com${flight.booking_link}`}
                target="_blank"
                rel="noreferrer"
            >
                Book Flight
            </a>
        </div>
    );
}