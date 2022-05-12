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

      <b-button
        type="is-primary"
        native-type="submit"
        expanded
        class="mt-5"
        :loading="submitButtonLoading"
        >Weiter</b-button
      >
    </form>
  </center-box-layout>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";
import { AuthChangeEmailResult } from "@/types/auth";
import { matchError } from "@/util/errors";

@Component({
  components: {
    CenterBoxLayout,
  },
})
export default class ChangeEmailView extends Vue {
  currentPassword = "";
  newEmail = "";
  submitButtonLoading = false;

  async submit() {
    let resp: AuthChangeEmailResult;
    this.submitButtonLoading = true;
    try {
      resp = await auth.changeEmail({
        email: this.newEmail,
        password: this.currentPassword,
      });
    } catch (err) {
      matchError(err, {
        invalid_password: "Das aktuelle Passwort ist inkorrekt.",
        email_exists: "Diese E-Mail-Adresse ist bereits in Verwendung.",
        rate_limit: "Zu viele Anfragen für diese E-Mail-Adresse.",
        default:
          "Beim Ändern der E-Mail-Adresse ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    } finally {
      this.submitButtonLoading = false;
    }
    this.$store.commit("setChangeEmailVerifyState", {
      changeEmailVerifyEmail: this.newEmail,
      changeEmailVerifyUuid: resp.uuid,
    });
    this.$router.push({ name: "ChangeEmailVerify" });
  }
}
</script>
