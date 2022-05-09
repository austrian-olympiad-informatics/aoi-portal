<template>
  <form action="" class="box" @submit.prevent="login">
    <h1 class="is-size-2 mb-3">Anmelden</h1>
    <b-field label="E-Mail-Adresse">
      <b-input
        type="email"
        placeholder="z.B. alice@gmail.com"
        v-model="email"
        required
      />
    </b-field>
    <b-field label="Passwort" class="mb-4">
      <b-input
        type="password"
        placeholder="********"
        v-model="password"
        required
      />
    </b-field>

    <b-button type="is-primary" native-type="submit" expanded
      >Anmelden</b-button
    >

    <p class="mt-5">
      Kein Konto?
      <router-link :to="{ name: 'Register' }">Hier registrieren</router-link>
    </p>
    <p class="mt-2">
      Passwort vergessen?
      <router-link :to="{ name: 'PasswordReset' }">Zurücksetzen</router-link>
    </p>
  </form>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import auth from "@/services/auth";
import { matchError } from "../util/errors";
import { AuthLoginResult } from "@/types/auth";

@Component
export default class LoginForm extends Vue {
  email = "";
  password = "";

  async login(): Promise<void> {
    let resp: AuthLoginResult;
    try {
      resp = await auth.login({
        email: this.email,
        password: this.password,
      });
    } catch (error) {
      matchError(error, {
        already_logged_in: "Du bist bereits angemeldet.",
        invalid_password: "Die E-Mail-Adresse und/oder das Passwort ist/sind falsch.",
        user_not_found: "Die E-Mail-Adresse und/oder das Passwort ist/sind falsch.",
        default: "Beim Anmelden ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      this.password = "";
      return;
    }

    this.$store.commit("setAuthToken", resp.token);
    await this.$store.dispatch("checkStatus");
    this.$emit("logged-in");
  }
}
</script>

<style scoped></style>
