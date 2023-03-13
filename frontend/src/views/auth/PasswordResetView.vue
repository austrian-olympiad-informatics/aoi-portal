<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="title is-2 mb-3">Passwort vergessen</h1>
      <b-field label="E-Mail-Adresse">
        <b-input
          v-model="email"
          type="email"
          placeholder="z.B. alice@gmail.com"
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
import { AuthRequestPasswordResetResult } from "@/types/auth";
import { matchError } from "@/util/errors";

@Component({
  components: {
    CenterBoxLayout,
  },
})
export default class PasswordResetView extends Vue {
  email = "";
  submitButtonLoading = false;

  async submit() {
    let resp: AuthRequestPasswordResetResult;
    this.submitButtonLoading = true;
    try {
      resp = await auth.requestPasswordReset({
        email: this.email,
      });
    } catch (err) {
      matchError(err, {
        user_not_found: "Diese E-Mail-Adresse ist noch nicht registriert.",
        rate_limit:
          "Zu viele Passwort zurücksetzen Anfragen für diese E-Mail-Adresse.",
        default:
          "Beim Passwort zurücksetzen ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    } finally {
      this.submitButtonLoading = false;
    }

    this.$store.commit("setPasswordResetVerifyState", {
      passwordResetVerifyEmail: this.email,
      passwordResetVerifyUuid: resp.uuid,
    });
    this.$router.push({ name: "PasswordResetVerify" });
  }
}
</script>
