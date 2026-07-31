import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost:8000/api",
});

export const searchFlights = async (data) => {
    const response = await api.post("/flights/search", data);
    return response.data;
};