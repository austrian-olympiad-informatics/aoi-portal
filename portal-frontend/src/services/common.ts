import axios, { AxiosInstance } from "axios";
const apiClient: AxiosInstance = axios.create({
  headers: {
    "Content-type": "application/json",
  },
});
export default apiClient;
