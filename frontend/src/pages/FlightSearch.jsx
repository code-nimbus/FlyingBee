import { useState } from "react";
import { searchFlights } from "../services/flightService";
import FlightCard from "../components/FlightCard";

export default function FlightSearch() {
    const [loading, setLoading] = useState(false);

    const [results, setResults] = useState([]);

    const [form, setForm] = useState({
        origin: "DEL",
        destination: "BOM",
        departure_date: "",

        return_date: "",

        adults: 1,
        children: 0,
        infants: 0,

        cabin_class: "economy",

        currency: "USD",

        direct_only: false,

        limit: 20,

        sort_by: "price",
    });

    const change = (e) => {
        const { name, value, type, checked } = e.target;

        setForm({
            ...form,
            [name]: type === "checkbox" ? checked : value,
        });
    };

    const submit = async (e) => {
        e.preventDefault();

        setLoading(true);

        try {
            const res = await searchFlights(form);

            setResults(res.flights);
        } catch (err) {
            console.log(err);
            alert("Unable to search");
        }

        setLoading(false);
    };

    return (
        <div style={{ padding: 40 }}>

            <h1>FlyingBee</h1>

            <form onSubmit={submit}>

                <input
                    name="origin"
                    value={form.origin}
                    onChange={change}
                    placeholder="Origin"
                />

                <input
                    name="destination"
                    value={form.destination}
                    onChange={change}
                    placeholder="Destination"
                />

                <br /><br />

                <input
                    type="date"
                    name="departure_date"
                    value={form.departure_date}
                    onChange={change}
                />

                <input
                    type="date"
                    name="return_date"
                    value={form.return_date}
                    onChange={change}
                />

                <br /><br />

                <input
                    type="number"
                    name="adults"
                    value={form.adults}
                    onChange={change}
                />

                <input
                    type="number"
                    name="children"
                    value={form.children}
                    onChange={change}
                />

                <input
                    type="number"
                    name="infants"
                    value={form.infants}
                    onChange={change}
                />

                <br /><br />

                <select
                    name="cabin_class"
                    value={form.cabin_class}
                    onChange={change}
                >
                    <option value="economy">Economy</option>

                    <option value="premium_economy">
                        Premium Economy
                    </option>

                    <option value="business">
                        Business
                    </option>

                    <option value="first">
                        First
                    </option>

                </select>

                <select
                    name="currency"
                    value={form.currency}
                    onChange={change}
                >
                    <option>USD</option>
                    <option>INR</option>
                    <option>EUR</option>
                    <option>GBP</option>
                </select>

                <br /><br />

                <label>

                    <input
                        type="checkbox"
                        name="direct_only"
                        checked={form.direct_only}
                        onChange={change}
                    />

                    Direct Flights Only

                </label>

                <br /><br />

                <select
                    name="sort_by"
                    value={form.sort_by}
                    onChange={change}
                >
                    <option value="price">
                        Cheapest
                    </option>

                    <option value="duration">
                        Fastest
                    </option>

                    <option value="departure">
                        Earliest Departure
                    </option>

                </select>

                <input
                    type="number"
                    name="limit"
                    value={form.limit}
                    onChange={change}
                />

                <br /><br />

                <button>
                    Search Flights
                </button>

            </form>

            <br />

            {loading && <h2>Searching...</h2>}

            {results.map((flight) => (
                <FlightCard
                    key={
                        flight.flight_number +
                        flight.departure_at
                    }
                    flight={flight}
                />
            ))}

        </div>
    );
}