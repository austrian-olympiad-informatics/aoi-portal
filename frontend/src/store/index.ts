import auth from "@/services/auth";
import { AuthStatusResult } from "@/types/auth";
import { createPinia, defineStore } from "pinia";

export const pinia = createPinia();

interface LocalStorageState {
  isAuthenticated: boolean;
  isAdmin: boolean;
  authToken: string;
  registerVerifyEmail: string;
  registerVerifyUuid: string;
  changeEmailVerifyEmail: string;
  changeEmailVerifyUuid: string;
  passwordResetVerifyEmail: string;
  passwordResetVerifyUuid: string;
  discordUsername: string;
}

export const useStore = defineStore("main", {
  state: () => ({
    authToken: "",
    isAuthenticated: false,
    isAdmin: false,
    firstName: "",
    lastName: "",
    registerVerifyEmail: "",
    registerVerifyUuid: "",
    changeEmailVerifyEmail: "",
    changeEmailVerifyUuid: "",
    passwordResetVerifyEmail: "",
    passwordResetVerifyUuid: "",
    discordUsername: "",
    isProxyAuth: false,
    proxyAuthError: false,
    proxyContestUuid: "",
    proxyContestName: "",
    proxyContestCmsName: "",
  }),
  getters: {
    getAuthToken: (state) => state.authToken,
  },
  actions: {
    setFromAuthStatus(status: AuthStatusResult) {
      this.isAuthenticated = status.authenticated;
      this.isAdmin = status.admin;
      this.firstName = status.first_name || "";
      this.lastName = status.last_name || "";
      this.discordUsername = status.discord_user || "";
      this.isProxyAuth = status.proxy_auth || false;
      this.proxyAuthError = status.proxy_auth_error || false;
      this.proxyContestUuid = status.proxy_contest?.uuid || "";
      this.proxyContestName = status.proxy_contest?.name || "";
      this.proxyContestCmsName = status.proxy_contest?.cms_name || "";
    },
    setAuthToken(authToken: string) {
      this.authToken = authToken;
    },
    setRegisterVerifyState({
      registerVerifyEmail,
      registerVerifyUuid,
    }: {
      registerVerifyEmail: string;
      registerVerifyUuid: string;
    }) {
      this.registerVerifyEmail = registerVerifyEmail;
      this.registerVerifyUuid = registerVerifyUuid;
    },
    setChangeEmailVerifyState({
      changeEmailVerifyEmail,
      changeEmailVerifyUuid,
    }: {
      changeEmailVerifyEmail: string;
      changeEmailVerifyUuid: string;
    }) {
      this.changeEmailVerifyEmail = changeEmailVerifyEmail;
      this.changeEmailVerifyUuid = changeEmailVerifyUuid;
    },
    setPasswordResetVerifyState({
      passwordResetVerifyEmail,
      passwordResetVerifyUuid,
    }: {
      passwordResetVerifyEmail: string;
      passwordResetVerifyUuid: string;
    }) {
      this.passwordResetVerifyEmail = passwordResetVerifyEmail;
      this.passwordResetVerifyUuid = passwordResetVerifyUuid;
    },
    setDiscordUsername(discordUsername: string) {
      this.discordUsername = discordUsername;
    },
    restoreState(savedState: LocalStorageState) {
      this.isAuthenticated = savedState.isAuthenticated;
      this.isAdmin = savedState.isAdmin;
      this.authToken = savedState.authToken;
      this.registerVerifyEmail = savedState.registerVerifyEmail;
      this.registerVerifyUuid = savedState.registerVerifyUuid;
      this.changeEmailVerifyEmail = savedState.changeEmailVerifyEmail;
      this.changeEmailVerifyUuid = savedState.changeEmailVerifyUuid;
      this.passwordResetVerifyEmail = savedState.passwordResetVerifyEmail;
      this.passwordResetVerifyUuid = savedState.passwordResetVerifyUuid;
      this.discordUsername = savedState.discordUsername;
    },
    async checkStatus() {
      const status = await auth.status();
      this.setFromAuthStatus(status);
    },
    loadLocalStorage() {
      const val = localStorage.getItem("aoiState");
      if (!val) return;
      const js = JSON.parse(val) as LocalStorageState;
      this.restoreState(js);
    },
    async init() {
      this.loadLocalStorage();
      await this.checkStatus();
    },
    _saveToLocalStorage() {
      const val: LocalStorageState = {
        isAuthenticated: this.isAuthenticated,
        isAdmin: this.isAdmin,
        authToken: this.authToken,
        registerVerifyEmail: this.registerVerifyEmail,
        registerVerifyUuid: this.registerVerifyUuid,
        changeEmailVerifyEmail: this.changeEmailVerifyEmail,
        changeEmailVerifyUuid: this.changeEmailVerifyUuid,
        passwordResetVerifyEmail: this.passwordResetVerifyEmail,
        passwordResetVerifyUuid: this.passwordResetVerifyUuid,
        discordUsername: this.discordUsername,
      };
      localStorage.setItem("aoiState", JSON.stringify(val));
    },
  },
});

// Persist state to localStorage on every change (except restoreState)
let _isRestoring = false;
const _origRestoreState = useStore.prototype?.restoreState;

pinia.use(({ store }) => {
  if (store.$id !== "main") return;
  store.$subscribe((mutation, state) => {
    if (_isRestoring) return;
    const val: LocalStorageState = {
      isAuthenticated: state.isAuthenticated,
      isAdmin: state.isAdmin,
      authToken: state.authToken,
      registerVerifyEmail: state.registerVerifyEmail,
      registerVerifyUuid: state.registerVerifyUuid,
      changeEmailVerifyEmail: state.changeEmailVerifyEmail,
      changeEmailVerifyUuid: state.changeEmailVerifyUuid,
      passwordResetVerifyEmail: state.passwordResetVerifyEmail,
      passwordResetVerifyUuid: state.passwordResetVerifyUuid,
      discordUsername: state.discordUsername,
    };
    localStorage.setItem("aoiState", JSON.stringify(val));
  }, { flush: "sync" });

  // Wrap restoreState to skip persistence during restore
  const origRestore = store.restoreState;
  store.restoreState = function (savedState: LocalStorageState) {
    _isRestoring = true;
    origRestore.call(this, savedState);
    _isRestoring = false;
  };
});
