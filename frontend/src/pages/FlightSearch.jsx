// import { useState } from "react";
// import { searchFlights } from "../services/flightService";
// import FlightCard from "../components/FlightCard";

// export default function FlightSearch() {
//     const [loading, setLoading] = useState(false);

//     const [results, setResults] = useState([]);

//     const [form, setForm] = useState({
//         origin: "DEL",
//         destination: "BOM",
//         departure_date: "",

//         return_date: "",

//         adults: 1,
//         children: 0,
//         infants: 0,

//         cabin_class: "economy",

//         currency: "USD",

//         direct_only: false,

//         limit: 20,

//         sort_by: "price",
//     });

//     const change = (e) => {
//         const { name, value, type, checked } = e.target;

//         setForm({
//             ...form,
//             [name]: type === "checkbox" ? checked : value,
//         });
//     };

//     const submit = async (e) => {
//         e.preventDefault();

//         setLoading(true);

//         try {
//             const res = await searchFlights(form);

//             setResults(res.flights || []);
//         } catch (err) {
//             console.log(err);
//             alert("Unable to search");
//         }

//         setLoading(false);
//     };

//     return (
//         <div style={{ padding: 40 }}>

//             <h1>FlyingBee</h1>

//             <form onSubmit={submit}>

//                 <input
//                     name="origin"
//                     value={form.origin}
//                     onChange={change}
//                     placeholder="Origin"
//                 />

//                 <input
//                     name="destination"
//                     value={form.destination}
//                     onChange={change}
//                     placeholder="Destination"
//                 />

//                 <br /><br />

//                 <input
//                     type="date"
//                     name="departure_date"
//                     value={form.departure_date}
//                     onChange={change}
//                 />

//                 <input
//                     type="date"
//                     name="return_date"
//                     value={form.return_date}
//                     onChange={change}
//                 />

//                 <br /><br />

//                 <input
//                     type="number"
//                     name="adults"
//                     value={form.adults}
//                     onChange={change}
//                 />

//                 <input
//                     type="number"
//                     name="children"
//                     value={form.children}
//                     onChange={change}
//                 />

//                 <input
//                     type="number"
//                     name="infants"
//                     value={form.infants}
//                     onChange={change}
//                 />

//                 <br /><br />

//                 <select
//                     name="cabin_class"
//                     value={form.cabin_class}
//                     onChange={change}
//                 >
//                     <option value="economy">Economy</option>

//                     <option value="premium_economy">
//                         Premium Economy
//                     </option>

//                     <option value="business">
//                         Business
//                     </option>

//                     <option value="first">
//                         First
//                     </option>

//                 </select>

//                 <select
//                     name="currency"
//                     value={form.currency}
//                     onChange={change}
//                 >
//                     <option>USD</option>
//                     <option>INR</option>
//                     <option>EUR</option>
//                     <option>GBP</option>
//                 </select>

//                 <br /><br />

//                 <label>

//                     <input
//                         type="checkbox"
//                         name="direct_only"
//                         checked={form.direct_only}
//                         onChange={change}
//                     />

//                     Direct Flights Only

//                 </label>

//                 <br /><br />

//                 <select
//                     name="sort_by"
//                     value={form.sort_by}
//                     onChange={change}
//                 >
//                     <option value="price">
//                         Cheapest
//                     </option>

//                     <option value="duration">
//                         Fastest
//                     </option>

//                     <option value="departure">
//                         Earliest Departure
//                     </option>

//                 </select>

//                 <input
//                     type="number"
//                     name="limit"
//                     value={form.limit}
//                     onChange={change}
//                 />

//                 <br /><br />

//                 <button>
//                     Search Flights
//                 </button>

//             </form>

//             <br />

//             {loading && <h2>Searching...</h2>}

//             {results.map((flight) => (
//                 <FlightCard
//                     key={
//                         flight.flight_number +
//                         flight.departure_at
//                     }
//                     flight={flight}
//                 />
//             ))}

//         </div>
//     );
// }

import { useState } from "react";
import { searchFlights, confirmFlightPrice, createFlightOrder } from "../services/flightService";
import FlightCard from "../components/FlightCard";

export default function FlightSearch() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState([]);
    const [selectedFlight, setSelectedFlight] = useState(null);
    const [bookingLoading, setBookingLoading] = useState(false);
    const [bookingResult, setBookingResult] = useState(null);

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

    const [traveler, setTraveler] = useState({
        first_name: "",
        last_name: "",
        date_of_birth: "",
        gender: "MALE",
        email: "",
        phone: "",
        passport_number: "",
        passport_expiry: "",
        nationality: "",
    });

    const change = (e) => {
        const { name, value, type, checked } = e.target;

        setForm({
            ...form,
            [name]: type === "checkbox" ? checked : value,
        });
    };

    const travelerChange = (e) => {
        const { name, value } = e.target;

        setTraveler({
            ...traveler,
            [name]: value,
        });
    };

    const submit = async (e) => {
        e.preventDefault();

        setLoading(true);
        setBookingResult(null);

        try {
            const res = await searchFlights(form);

            setResults(res.flights || []);
        } catch (err) {
            console.log(err);
            alert("Unable to search");
        } finally {
            setLoading(false);
        }
    };

    const selectFlight = (flight) => {
        setSelectedFlight(flight);
        setBookingResult(null);

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth",
        });
    };

    const bookFlight = async (e) => {
        e.preventDefault();

        if (!selectedFlight) {
            return;
        }

        setBookingLoading(true);

        try {
            // First confirm the selected price
            const priceResponse = await confirmFlightPrice(selectedFlight);

            const confirmedFlight =
                priceResponse.data || selectedFlight;

            // Then create the local booking/order
            const booking = await createFlightOrder({
                flight: confirmedFlight,
                traveler,
            });

            setBookingResult(booking);

        } catch (err) {
            console.log(err);

            alert(
                err?.response?.data?.detail ||
                "Unable to create booking"
            );
        } finally {
            setBookingLoading(false);
        }
    };

    return (
        <div style={{ padding: 40 }}>

            <h1>FlyingBee</h1>

            {/* =========================
                SEARCH
            ========================== */}

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
                    min="1"
                    value={form.adults}
                    onChange={change}
                />

                <input
                    type="number"
                    name="children"
                    min="0"
                    value={form.children}
                    onChange={change}
                />

                <input
                    type="number"
                    name="infants"
                    min="0"
                    value={form.infants}
                    onChange={change}
                />

                <br /><br />

                <select
                    name="cabin_class"
                    value={form.cabin_class}
                    onChange={change}
                >
                    <option value="economy">
                        Economy
                    </option>

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
                    min="1"
                    max="100"
                    value={form.limit}
                    onChange={change}
                />

                <br /><br />

                <button type="submit">
                    Search Flights
                </button>

            </form>

            <br />

            {loading && <h2>Searching...</h2>}

            {/* =========================
                FLIGHT RESULTS
            ========================== */}

            {results.map((flight) => (
                <div key={
                    flight.flight_number +
                    flight.departure_at
                }>

                    <FlightCard flight={flight} />

                    <button
                        onClick={() => selectFlight(flight)}
                    >
                        Select Flight
                    </button>

                </div>
            ))}

            {/* =========================
                TRAVELER INFORMATION
            ========================== */}

            {selectedFlight && (
                <div style={{ marginTop: 40 }}>

                    <h2>Traveler Information</h2>

                    <p>
                        {selectedFlight.airline}{" "}
                        {selectedFlight.flight_number}
                    </p>

                    <p>
                        {selectedFlight.origin} →{" "}
                        {selectedFlight.destination}
                    </p>

                    <p>
                        Price:{" "}
                        {selectedFlight.currency || form.currency}{" "}
                        {selectedFlight.price}
                    </p>

                    <form onSubmit={bookFlight}>

                        <input
                            name="first_name"
                            placeholder="First Name"
                            value={traveler.first_name}
                            onChange={travelerChange}
                            required
                        />

                        <input
                            name="last_name"
                            placeholder="Last Name"
                            value={traveler.last_name}
                            onChange={travelerChange}
                            required
                        />

                        <br /><br />

                        <label>
                            Date of Birth
                        </label>

                        <input
                            type="date"
                            name="date_of_birth"
                            value={traveler.date_of_birth}
                            onChange={travelerChange}
                            required
                        />

                        <select
                            name="gender"
                            value={traveler.gender}
                            onChange={travelerChange}
                        >
                            <option value="MALE">
                                Male
                            </option>

                            <option value="FEMALE">
                                Female
                            </option>
                        </select>

                        <br /><br />

                        <input
                            type="email"
                            name="email"
                            placeholder="Email"
                            value={traveler.email}
                            onChange={travelerChange}
                            required
                        />

                        <input
                            name="phone"
                            placeholder="Phone"
                            value={traveler.phone}
                            onChange={travelerChange}
                            required
                        />

                        <br /><br />

                        <input
                            name="nationality"
                            placeholder="Nationality"
                            value={traveler.nationality}
                            onChange={travelerChange}
                            required
                        />

                        <input
                            name="passport_number"
                            placeholder="Passport Number"
                            value={traveler.passport_number}
                            onChange={travelerChange}
                        />

                        <input
                            type="date"
                            name="passport_expiry"
                            value={traveler.passport_expiry}
                            onChange={travelerChange}
                        />

                        <br /><br />

                        <button
                            type="submit"
                            disabled={bookingLoading}
                        >
                            {bookingLoading
                                ? "Creating Booking..."
                                : "Confirm & Book Flight"}
                        </button>

                    </form>
                </div>
            )}

            {/* =========================
                BOOKING RESULT
            ========================== */}

            {bookingResult && (
                <div style={{ marginTop: 40 }}>

                    <h2>Booking Created</h2>

                    <p>
                        Booking ID:{" "}
                        {bookingResult.order_id}
                    </p>

                    <p>
                        Status:{" "}
                        {bookingResult.status}
                    </p>

                    <p>
                        {bookingResult.message}
                    </p>

                </div>
            )}

        </div>
    );
}