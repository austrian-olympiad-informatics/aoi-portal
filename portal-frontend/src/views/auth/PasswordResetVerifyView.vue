<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-5">
          <form
            class="box"
            @submit.prevent="passwordResetVerify"
            v-if="stageVerifyMail"
          >
            <h1 class="is-size-3 mb-3">Wir haben dir einen Code gesendet</h1>
            <p>
              Gib ihn unten zum Zurücksetzen des Passworts von {{ email }} ein.
            </p>
            <b-field
              class="mt-4 mb-4"
              label="Verifizierungscode"
              label-position="inside"
            >
              <b-input
                v-model="verifyCode"
                inputmode="numeric"
                pattern="[0-9]*"
                size="is-medium"
                required
                key="verification-code"
              />
            </b-field>

            <b-button type="is-primary" native-type="submit" expanded
              >Weiter</b-button
            >
          </form>

          <form
            class="box"
            @submit.prevent="passwordResetComplete"
            v-if="!stageVerifyMail"
          >
            <h1 class="is-size-3 mb-3">Neues Passwort setzen</h1>
            <b-field label="Neues Passwort festlegen">
              <b-input
                v-model="newPassword"
                type="password"
                placeholder="********"
                minlength="8"
                required
                key="new-password"
              />
            </b-field>
            <b-field
              label="Neues Passwort bestätigen"
              :type="{ 'is-danger': !newPasswordsMatch }"
              :message="{
                'Passwörter müssen übereinstimmen': !newPasswordsMatch,
              }"
              key="new-password-confirm"
            >
              <b-input
                v-model="newPasswordConfirm"
                type="password"
                placeholder="********"
                minlength="8"
                required
              />
            </b-field>

            <b-button type="is-primary" native-type="submit" expanded
              >Weiter</b-button
            >
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { AuthResetPasswordResult } from "@/types/auth";
import { matchError } from "@/util/errors";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class PasswordResetVerifyView extends Vue {
  verifyCode = "";
  stageVerifyMail = true;
  newPassword = "";
  newPasswordConfirm = "";

  get email(): string {
    return this.$store.getters.passwordResetVerifyEmail;
  }
  get newPasswordsMatch(): boolean {
    return this.newPassword === this.newPasswordConfirm;
  }

  async passwordResetVerify() {
    await auth.resetPassword({
      uuid: this.$store.getters.passwordResetVerifyUuid,
      verification_code: this.verifyCode,
    });
    this.stageVerifyMail = false;
  }
  async passwordResetComplete() {
    if (!this.newPasswordsMatch) return;
    let resp: AuthResetPasswordResult;
    try {
      resp = await auth.resetPassword({
        uuid: this.$store.getters.passwordResetVerifyUuid,
        verification_code: this.verifyCode,
        new_password: this.newPassword,
      });
    } catch (err) {
      matchError(err, {
        no_longer_valid: "Dieser Verifizierungscode ist nicht mehr gültig.",
        too_many_attempts: "Zu viele falsche Versuche.",
        invalid_verification_code:
          "Der Verifizierunscode ist nicht korrekt. Bitte versuche es erneut.",
        default:
          "Beim Verifizieren ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    }
    this.$store.commit("setAuthToken", resp.token);
    this.$store.commit("setPasswordResetVerifyState", {
      passwordResetVerifyEmail: "",
      passwordResetVerifyUuid: "",
    });
    await this.$store.dispatch("checkStatus");
    this.$buefy.toast.open({
      message: "Passwort wurde erfolgreich zurückgesetzt!",
      type: "is-success",
    });
    this.$router.push("/");
  }
  mounted(): void {
    if (!this.$store.getters.passwordResetVerifyUuid) {
      this.$router.push("/");
    }
  }
}
</script>
