import axios from "axios";

const API_URL = `http://${window.location.hostname}:8000`;

const api = axios.create({
    baseURL: API_URL,
});

api.interceptors.request.use(async (config) => {
    let accessToken = localStorage.getItem("accessToken");
    const refreshToken = localStorage.getItem("refreshToken");

    if (!accessToken && refreshToken) {
        try {
            const { data } = await axios.post("/token/refresh/", { refresh: refreshToken });
            accessToken = data.access;
            localStorage.setItem("accessToken", accessToken);
        } catch (err) {
            console.warn("Refresh token invalid");
            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
        }
    }

    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
});

export const AuthAPI = {
    login: async (username, password) => {
        const { data } = await api.post("/token/", {
            username,
            password,
        });
        localStorage.setItem("accessToken", data.access);
        localStorage.setItem("refreshToken", data.refresh);
        return data;
    },

    logout: () => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
    },
};

export const SignatureAPI = {
    sign: async (data) => {
        const response = await api.post("/sign/", data);
        return response.data;
    },

    verify: async (data) => {
        const response= await api.post("/verify/", data);
        return response.data;
    }
}