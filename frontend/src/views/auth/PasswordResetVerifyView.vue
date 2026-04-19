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
            <h1 class="title is-3 mb-3">Wir haben dir einen Code gesendet</h1>
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
            <h1 class="title is-3 mb-3">Neues Passwort setzen</h1>
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

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "@/store";
import { useToast } from "buefy";
import auth from "@/services/auth";
import { AuthResetPasswordResult } from "@/types/auth";
import { matchError } from "@/util/errors";

const router = useRouter();
const store = useStore();
const toast = useToast();

const verifyCode = ref("");
const stageVerifyMail = ref(true);
const newPassword = ref("");
const newPasswordConfirm = ref("");

const email = computed(() => store.passwordResetVerifyEmail);
const newPasswordsMatch = computed(
  () => newPassword.value === newPasswordConfirm.value,
);

async function passwordResetVerify() {
  await auth.resetPassword({
    uuid: store.passwordResetVerifyUuid,
    verification_code: verifyCode.value,
  });
  stageVerifyMail.value = false;
}

async function passwordResetComplete() {
  if (!newPasswordsMatch.value) return;
  let resp: AuthResetPasswordResult;
  try {
    resp = await auth.resetPassword({
      uuid: store.passwordResetVerifyUuid,
      verification_code: verifyCode.value,
      new_password: newPassword.value,
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
  store.setAuthToken(resp.token);
  store.setPasswordResetVerifyState({
    passwordResetVerifyEmail: "",
    passwordResetVerifyUuid: "",
  });
  await store.checkStatus();
  toast.open({
    message: "Passwort wurde erfolgreich zurückgesetzt!",
    type: "is-success",
  });
  router.push("/");
}

onMounted((): void => {
  if (!store.passwordResetVerifyUuid) {
    router.push("/");
  }
});
</script>
