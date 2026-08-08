// import axios from "axios";


// const api = axios.create({

//     baseURL: "http://localhost:8000/api"

// });



// export async function searchFlights(data) {

//     const response = await api.post(
//         "/flights/search",
//         data
//     );


//     return response.data;

// }

// export const createFlightOrder = async (data) => {

//     const response = await api.post(
//         "/booking/flight-orders",
//         data
//     );


//     return response.data;

// };
// // import axios from "axios";

// // const api = axios.create({
// //     baseURL: "http://localhost:8000/api",
// // });

// // export const searchFlights = async (data) => {
// //     const response = await api.post("/flights/search", data);
// //     return response.data;
// // };

import axios from "axios";

const API_URL = "http://localhost:8000/api";

export const searchFlights = async (params) => {
    const response = await axios.get(
        `${API_URL}/shopping/flight-offers`,
        {
            params,
        }
    );

    return response.data;
};


export const confirmFlightPrice = async (flight) => {
    const response = await axios.post(
        `${API_URL}/shopping/flight-offers/pricing`,
        flight
    );

    return response.data;
};


export const createFlightOrder = async ({
    flight,
    traveler,
}) => {
    const response = await axios.post(
        `${API_URL}/booking/flight-orders`,
        {
            flight,
            traveler,
        }
    );

    return response.data;
};