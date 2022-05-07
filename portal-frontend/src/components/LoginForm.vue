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
      Kein Konto? <router-link :to="{ name: 'Register' }">Hier registrieren</router-link>
    </p>
    <p class="mt-2">
      Passwort vergessen?
      <router-link :to="{ name: 'PasswordReset' }">Zurücksetzen</router-link>
    </p>
  </form>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { NotificationProgrammatic as Notification } from "buefy";
import auth from "@/services/auth";

@Component
export default class LoginForm extends Vue {
  email = "";
  password = "";

  async login(): Promise<void> {

    try {
      const resp = await auth.login({
        email: this.email,
        password: this.password,
      });

      this.$store.commit("setAuthToken", resp.token);
      let result = await this.$store.dispatch("checkStatus");

      if(!result.isAuthenticated) {
        Notification.open({
          message: "Die E-Mail-Adresse und/oder das Passwort ist/sind falsch.",
          type: "is-danger",
          position: "is-top-right",
        });
      }

      this.$emit("logged-in");

    } catch(except) {
        Notification.open({
          message: "Beim Anmelden ist etwas schiefgelaufen. Bitte versuche es später erneut.",
          type: "is-danger",
          position: "is-top-right",
        });
    }
  }
}
</script>

<style scoped></style>
