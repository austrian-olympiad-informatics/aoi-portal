import auth from "@/services/auth";
import { AuthStatusResult } from "@/types/auth";
import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

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

const store = new Vuex.Store({
  state: {
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
  },
  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    isAdmin: (state) => state.isAdmin,
    getAuthToken: (state) => state.authToken,
    registerVerifyEmail: (state) => state.registerVerifyEmail,
    registerVerifyUuid: (state) => state.registerVerifyUuid,
    changeEmailVerifyEmail: (state) => state.changeEmailVerifyEmail,
    changeEmailVerifyUuid: (state) => state.changeEmailVerifyUuid,
    passwordResetVerifyEmail: (state) => state.passwordResetVerifyEmail,
    passwordResetVerifyUuid: (state) => state.passwordResetVerifyUuid,
    firstName: (state) => state.firstName,
    lastName: (state) => state.lastName,
    discordUsername: (state) => state.discordUsername,
  },
  mutations: {
    setFromAuthStatus(state, status: AuthStatusResult) {
      state.isAuthenticated = status.authenticated;
      state.isAdmin = status.admin;
      state.firstName = status.first_name || "";
      state.lastName = status.last_name || "";
      state.discordUsername = status.discord_user || "";
    },
    setAuthToken(state, authToken: string) {
      state.authToken = authToken;
    },
    setRegisterVerifyState(state, { registerVerifyEmail, registerVerifyUuid }) {
      state.registerVerifyEmail = registerVerifyEmail;
      state.registerVerifyUuid = registerVerifyUuid;
    },
    setChangeEmailVerifyState(
      state,
      { changeEmailVerifyEmail, changeEmailVerifyUuid }
    ) {
      state.changeEmailVerifyEmail = changeEmailVerifyEmail;
      state.changeEmailVerifyUuid = changeEmailVerifyUuid;
    },
    setPasswordResetVerifyState(
      state,
      { passwordResetVerifyEmail, passwordResetVerifyUuid }
    ) {
      state.passwordResetVerifyEmail = passwordResetVerifyEmail;
      state.passwordResetVerifyUuid = passwordResetVerifyUuid;
    },
    setDiscordUsername(state, discordUsername: string) {
      state.discordUsername = discordUsername;
    },
    restoreState(state, savedState: LocalStorageState) {
      state.isAuthenticated = savedState.isAuthenticated;
      state.isAdmin = savedState.isAdmin;
      state.authToken = savedState.authToken;
      state.registerVerifyEmail = savedState.registerVerifyEmail;
      state.registerVerifyUuid = savedState.registerVerifyUuid;
      state.changeEmailVerifyEmail = savedState.changeEmailVerifyEmail;
      state.changeEmailVerifyUuid = savedState.changeEmailVerifyUuid;
      state.passwordResetVerifyEmail = savedState.passwordResetVerifyEmail;
      state.passwordResetVerifyUuid = savedState.passwordResetVerifyUuid;
      state.discordUsername = savedState.discordUsername;
    },
  },
  actions: {
    async checkStatus({ commit }) {
      const status = await auth.status();
      commit("setFromAuthStatus", status);
    },
    loadLocalStorage({ commit }) {
      const val = localStorage.getItem("aoiState");
      if (!val) return;
      const js = JSON.parse(val) as LocalStorageState;
      commit("restoreState", js);
    },
    async init({ dispatch }) {
      dispatch("loadLocalStorage");
      await dispatch("checkStatus");
    },
  },
  modules: {},
});
store.subscribe((mutation, state) => {
  if (mutation.type !== "restoreState") {
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
  }
});

export default store;
