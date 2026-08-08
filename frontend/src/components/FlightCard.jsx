import { FaPlane, FaClock } from "react-icons/fa";
import { createFlightOrder } from "../services/flightService";

export default function FlightCard({ flight }) {


    const formatTime = (date) => {

        return new Date(date)
            .toLocaleTimeString(
                [],
                {
                    hour: "2-digit",
                    minute: "2-digit"
                }
            )

    }



    const duration = (minutes) => {

        if (!minutes)
            return "N/A";


        const h = Math.floor(minutes / 60);

        const m = minutes % 60;


        return `${h}h ${m}m`;

    }




    return (

        <div className="bg-white rounded-2xl shadow-lg border p-6 mb-6 hover:shadow-xl transition">
            <div className="flex justify-between items-center ">
                <div>
                    <div className="
flex
items-center
gap-3
">

                        <div className="
bg-blue-600
text-white
rounded-lg
px-3
py-2
font-bold
">

                            {flight.airline}

                        </div>


                        <h2 className="
text-xl
font-bold
">

                            {flight.flight_number}

                        </h2>


                    </div>


                </div>



                <div className="
text-3xl
font-bold
text-blue-600
">

                    ${flight.price}

                </div>


            </div>



            <hr className="my-5" />



            <div className="
flex
items-center
justify-between
">


                <div className="text-center">

                    <h2 className="text-2xl font-bold">

                        {formatTime(
                            flight.departure_at
                        )}

                    </h2>


                    <p>
                        {flight.origin}
                    </p>

                </div>



                <div className="
flex-1
px-8
text-center
">


                    <div className="
flex
justify-center
gap-2
items-center
text-gray-500
">

                        <FaClock />

                        {duration(
                            flight.duration
                        )}

                    </div>



                    <div className="
border-t
border-dashed
mt-3
relative
">

                        <FaPlane
                            className="
absolute
left-1/2
-top-3
text-blue-500
"
                        />


                    </div>


                    <p className="mt-2">

                        {
                            flight.transfers === 0
                                ?
                                "Direct"
                                :
                                `${flight.transfers} stop`
                        }

                    </p>


                </div>




                <div className="text-center">


                    <h2 className="text-2xl font-bold">

                        {flight.destination}

                    </h2>


                </div>



            </div>




            <button
                onClick={() =>
                    createFlightOrder({
                        flight_number: flight.flight_number,
                        airline: flight.airline,
                        origin: flight.origin,
                        destination: flight.destination,
                        departure_at: flight.departure_at,
                        price: flight.price,
                        currency: "USD",
                        booking_link: flight.booking_link
                    })
                }
            >
                Create Booking
            </button>



        </div>

    )

}

// export default function FlightCard({ flight }) {
//     return (
//         <div
//             style={{
//                 border: "1px solid #ddd",
//                 borderRadius: 10,
//                 padding: 20,
//                 marginBottom: 20,
//             }}
//         >
//             <h3>{flight.airline}</h3>

//             <p>
//                 <strong>Flight:</strong> {flight.flight_number}
//             </p>

//             <p>
//                 {flight.origin} ➜ {flight.destination}
//             </p>

//             <p>
//                 Departure:
//                 {" "}
//                 {new Date(flight.departure_at).toLocaleString()}
//             </p>

//             <p>
//                 Duration:
//                 {" "}
//                 {flight.duration}
//                 {" "}minutes
//             </p>

//             <p>
//                 Stops:
//                 {" "}
//                 {flight.transfers}
//             </p>

//             <h2>${flight.price}</h2>

//             <a
//                 href={`https://www.travelpayouts.com${flight.booking_link}`}
//                 target="_blank"
//                 rel="noreferrer"
//             >
//                 Book Flight
//             </a>
//         </div>
//     );
// }