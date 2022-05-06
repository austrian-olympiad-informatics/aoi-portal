import axios, { AxiosInstance } from "axios";
import store from "@/store/index";
const apiClient: AxiosInstance = axios.create({
  headers: {
    "Content-type": "application/json",
  },
});
const updateAuthToken = (authToken: string) => {
  if (authToken) {
    apiClient.defaults.headers.common = {
      "Authorization": `Bearer ${authToken}`,
    };
  } else {
    apiClient.defaults.headers.common = {};
  }
};
store.subscribe((mutation, state) => {
  if (mutation.type === "setAuthToken" || mutation.type === "restoreState") {
    updateAuthToken(state.authToken);
  }
});
export default apiClient;
