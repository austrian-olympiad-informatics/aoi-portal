<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-5">

          <form class="box" @submit.prevent="changeEmailVerify">
            <h1 class="is-size-3 mb-3">Wir haben dir einen Code gesendet</h1>
            <p>
              Gib ihn unten zur Verifizierung von {{ newMail }} ein.
            </p>
            <b-field class="mt-4 mb-4" label="Verifizierungscode" label-position="inside">
              <b-input
                v-model="verifyCode"
                inputmode="numeric"
                pattern="[0-9]*" 
                size="is-medium"
                required />
            </b-field>

            <b-button type="is-primary" native-type="submit" expanded>Weiter</b-button>
          </form>

        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { matchError } from "@/util/errors";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class ChangeEmailVerifyView extends Vue {
  verifyCode: string = "";

  get newMail(): string {
    return this.$store.getters.changeEmailVerifyEmail;
  }

  async changeEmailVerify() {
    try {
      await auth.changeEmailVerify({
      uuid: this.$store.getters.changeEmailVerifyUuid,
      verification_code: this.verifyCode,
    });
    } catch (err) {
      matchError(err, {
        no_longer_valid: "Dieser Verifizierungscode ist nicht mehr gültig.",
        too_many_attempts: "Zu viele falsche Versuche.",
        invalid_verification_code: "Der Verifizierunscode ist nicht korrekt. Bitte versuche es erneut.",
        default: "Beim Verifizieren ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    }
    
    this.$store.commit("setChangeEmailVerifyState", {
      changeEmailVerifyEmail: "",
      changeEmailVerifyUuid: "",
    });
    await this.$store.dispatch("checkStatus");
    this.$buefy.toast.open({
      message: "E-Mail-Adresse erfolgreich geändert!",
      type: "is-success",
    });
    this.$router.push("/");
  }
  mounted(): void {
    if (!this.$store.getters.changeEmailVerifyUuid) {
      this.$router.push("/");
    }
  }
}
</script>
