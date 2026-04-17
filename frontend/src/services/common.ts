import axios, { AxiosInstance } from "axios";
import { useStore } from "@/store/index";
import { watch } from "vue";
const apiClient: AxiosInstance = axios.create({
  headers: {
    "Content-type": "application/json",
  },
});
const updateAuthToken = (authToken: string) => {
  if (authToken) {
    apiClient.defaults.headers.common = {
      Authorization: `Bearer ${authToken}`,
    };
  } else {
    apiClient.defaults.headers.common = {};
  }
};

export function initApiClient() {
  const store = useStore();
  // Set initial token
  updateAuthToken(store.authToken);
  // Watch for changes
  watch(
    () => store.authToken,
    (newToken) => updateAuthToken(newToken),
  );
}

export default apiClient;
