<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="title is-3 mb-3">E-Mail-Adresse ändern</h1>
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

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import auth from "@/services/auth";
import { useStore } from "@/store";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";
import { AuthChangeEmailResult } from "@/types/auth";
import { matchError } from "@/util/errors";

const router = useRouter();
const store = useStore();

const currentPassword = ref("");
const newEmail = ref("");
const submitButtonLoading = ref(false);

async function submit() {
  let resp: AuthChangeEmailResult;
  submitButtonLoading.value = true;
  try {
    resp = await auth.changeEmail({
      email: newEmail.value,
      password: currentPassword.value,
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
    submitButtonLoading.value = false;
  }
  store.setChangeEmailVerifyState({
    changeEmailVerifyEmail: newEmail.value,
    changeEmailVerifyUuid: resp.uuid,
  });
  router.push({ name: "ChangeEmailVerify" });
}
</script>
