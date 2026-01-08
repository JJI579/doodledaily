import axios, { AxiosError, type AxiosInstance } from 'axios';
import router from './router';

const debug: boolean = true;
const BASE_URL = debug ? 'http://127.0.0.1:8000' : 'https://pibble.pics/api';

const api: AxiosInstance = axios.create({
	baseURL: BASE_URL,
	withCredentials: true, // if using cookies
});

// Optional: Add request interceptor to attach token
api.interceptors.request.use((config) => {
	const token = localStorage.getItem('token');
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

// Optional: Add response interceptor to handle 401 globally
api.interceptors.response.use(
	(response) => response,
	async (error: AxiosError & { config?: any }) => {
		const originalRequest = error.config;
		if (!originalRequest) return Promise.reject(error);
		console.log("having to do this")
		if (error.response?.status === 401 && !originalRequest._retry) {
			originalRequest._retry = true; console.log("here?")

			try {
				// Call refresh endpoint
				const refreshToken = localStorage.getItem('refresh_token');
				if (refreshToken === null) {
					localStorage.removeItem('token');
					localStorage.removeItem('refresh_token');
					router.push({ name: 'login' });
					return Promise.reject();
				}
				const { data } = await axios.post(
					`${BASE_URL}/refresh`,
					{
						token: localStorage.getItem('refresh_token'),
					},
					{ withCredentials: true }
				);

				localStorage.setItem('token', data.access_token);
				originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
				return api(originalRequest);
			} catch (err) {
				// TODO: redirect to login
				localStorage.removeItem('token');
				localStorage.removeItem('refresh_token');
				console.error('Refresh token failed', err);
				return Promise.reject(err);
			}
		}

		return Promise.reject(error);
	}
);
export default api;
