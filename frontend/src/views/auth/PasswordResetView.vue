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

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import auth from "@/services/auth";
import { useStore } from "@/store";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";
import { AuthRequestPasswordResetResult } from "@/types/auth";
import { matchError } from "@/util/errors";

const router = useRouter();
const store = useStore();

const email = ref("");
const submitButtonLoading = ref(false);

async function submit() {
  let resp: AuthRequestPasswordResetResult;
  submitButtonLoading.value = true;
  try {
    resp = await auth.requestPasswordReset({
      email: email.value,
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
    submitButtonLoading.value = false;
  }

  store.setPasswordResetVerifyState({
    passwordResetVerifyEmail: email.value,
    passwordResetVerifyUuid: resp.uuid,
  });
  router.push({ name: "PasswordResetVerify" });
}
</script>
