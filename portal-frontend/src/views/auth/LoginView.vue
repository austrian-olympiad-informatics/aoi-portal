<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="title is-3 mb-3">Anmelden</h1>
      <LoginInput v-model="data" />
      <b-button type="is-primary" native-type="submit" expanded
        >Anmelden</b-button
      >
    </form>

    <p class="mt-5">
      Kein Konto?
      <router-link :to="{ name: 'Register' }"
        >Hier registrieren</router-link
      >
    </p>
    <p class="mt-2">
      Passwort vergessen?
      <router-link :to="{ name: 'PasswordReset' }"
        >Zurücksetzen</router-link
      >
    </p>
    <div class="is-divider" data-content="ODER"></div>
    <router-link
      class="button is-rounded is-fullwidth"
      type="button"
      :to="{ name: 'GitHubOAuth' }"
    >
      <span class="icon">
        <img src="../../assets/github-icon.svg" loading="lazy" />
      </span>
      Mit GitHub anmelden
    </router-link>
    <!--
    <router-link
      class="button is-rounded is-fullwidth mt-2"
      type="button"
      :to="{ name: 'GoogleOAuth' }"
    >
      <span class="icon">
        <img src="../../assets/google-icon.svg" loading="lazy" />
      </span>
      Mit Google anmelden
    </router-link>
    -->
  </center-box-layout>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import LoginInput, { LoginInputData } from "@/components/LoginInput.vue";
import { AuthLoginResult } from "@/types/auth";
import auth from "@/services/auth";
import { matchError } from "@/util/errors";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

@Component({
  components: {
    LoginInput,
    CenterBoxLayout,
  },
})
export default class LoginView extends Vue {
  data: LoginInputData = {
    email: "",
    password: "",
  };
  mounted(): void {
    if (this.$store.getters.isAuthenticated) {
      this.$router.push("/");
    }
  }

  async submit(): Promise<void> {
    let resp: AuthLoginResult;
    try {
      resp = await auth.login({
        email: this.data.email,
        password: this.data.password,
      });
    } catch (error) {
      matchError(error, {
        already_logged_in: "Du bist bereits angemeldet.",
        invalid_password:
          "Die E-Mail-Adresse und/oder das Passwort ist/sind falsch.",
        user_not_found:
          "Die E-Mail-Adresse und/oder das Passwort ist/sind falsch.",
        default:
          "Beim Anmelden ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      this.data.password = "";
      return;
    }

    this.$store.commit("setAuthToken", resp.token);
    await this.$store.dispatch("checkStatus");
    this.$buefy.toast.open({
      message: "Erfolgreich angemeldet!",
      type: "is-success",
    });
    this.$router.push("/");
  }
}
</script>

<style scoped>
.is-divider {
  display: block;
  position: relative;
  border-top: 0.1rem solid #dbdbdb;
  height: 0.1rem;
  margin: 2rem 0;
  text-align: center;
}
.is-divider::after {
  background: #fff;
  color: #b5b5b5;
  content: attr(data-content);
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  transform: translateY(-1.1rem);
  text-align: center;
}

.button .icon {
  margin-right: 0.5em !important;
}
.button .icon img {
  height: 1.5em;
  display: inline-block;
}
</style>
