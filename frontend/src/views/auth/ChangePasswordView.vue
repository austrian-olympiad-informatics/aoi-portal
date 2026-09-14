<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="title is-3 mb-3">Passwort ändern</h1>
      <b-field label="Aktuelles Passwort">
        <b-input
          v-model="currentPassword"
          type="password"
          placeholder="Aktuelles Passwort"
          required
        />
      </b-field>
      <b-field label="Neues Passwort festlegen">
        <b-input
          v-model="newPassword"
          type="password"
          placeholder="********"
          minlength="8"
          required
        />
      </b-field>
      <b-field
        label="Neues Passwort bestätigen"
        :type="{ 'is-danger': !newPasswordsMatch }"
        :message="{
          'Passwörter müssen übereinstimmen': !newPasswordsMatch,
        }"
      >
        <b-input
          v-model="newPasswordConfirm"
          type="password"
          placeholder="********"
          minlength="8"
          required
        />
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded class="mt-5"
        >Speichern</b-button
      >
    </form>
  </center-box-layout>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "buefy";
import auth from "@/services/auth";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";
import { matchError } from "@/util/errors";

const router = useRouter();
const toast = useToast();

const currentPassword = ref("");
const newPassword = ref("");
const newPasswordConfirm = ref("");

const newPasswordsMatch = computed(
  () => newPassword.value === newPasswordConfirm.value,
);

async function submit() {
  if (!newPasswordsMatch.value) return;
  try {
    await auth.changePassword({
      old_password: currentPassword.value,
      new_password: newPassword.value,
    });
  } catch (err) {
    matchError(err, {
      invalid_password: "Das aktuelle Passwort ist inkorrekt.",
      default:
        "Beim Passwort Ändern ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    });
    return;
  }
  toast.open({
    message: "Passwort geändert!",
    type: "is-success",
  });
  router.push({ name: "Profile" });
}
</script>
