<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="is-size-2 mb-3">E-Mail-Adresse ändern</h1>
      <b-field label="Neue E-Mail-Adresse">
        <b-input
          v-model="newEmail"
          type="email"
          placeholder="z.B. alice@gmail.com"
          required
        />
      </b-field>
      <b-field label="Aktuelles Passwort zur Bestätigung">
        <b-input
          v-model="currentPassword"
          type="password"
          placeholder="Aktuelles Passwort"
          required
        />
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded class="mt-5"
        >Weiter</b-button
      >
    </form>
  </center-box-layout>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

@Component({
  components: {
    CenterBoxLayout,
  },
})
export default class ChangeEmailView extends Vue {
  currentPassword: string = "";
  newEmail: string = "";

  async submit() {
    const resp = await auth.changeEmail({
      email: this.newEmail,
      password: this.currentPassword,
    });
    this.$store.commit("setChangeEmailVerifyState", {
      changeEmailVerifyEmail: this.newEmail,
      changeEmailVerifyUuid: resp.uuid,
    });
    this.$router.push({ name: "ChangeEmailVerify" });
  }
}
</script>
