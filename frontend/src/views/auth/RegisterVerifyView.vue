<template>
  <center-box-layout>
    <form @submit.prevent="registerVerify">
      <h1 class="title is-3 mb-3">Wir haben dir einen Code gesendet</h1>
      <p>Gib ihn unten zur Verifizierung von {{ registerEmail }} ein.</p>
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
        />
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded
        >Weiter</b-button
      >

      <p class="mt-5" v-if="showHelpText">
        Keine Mail erhalten? Kontaktiere uns unter
        <a href="mailto:orga@informatikolympiade.at"
          >orga@informatikolympiade.at</a
        >
      </p>
    </form>
  </center-box-layout>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "@/store";
import { useToast } from "buefy";
import auth from "@/services/auth";
import { AuthRegisterVerifyResult } from "@/types/auth";
import { matchError } from "@/util/errors";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

const router = useRouter();
const store = useStore();
const toast = useToast();

const verifyCode = ref("");
const showHelpText = ref(false);

const registerEmail = computed(() => store.registerVerifyEmail);

async function registerVerify() {
  let resp: AuthRegisterVerifyResult;
  try {
    resp = await auth.registerVerify({
      uuid: store.registerVerifyUuid,
      verification_code: verifyCode.value,
    });
  } catch (err) {
    matchError(err, {
      // TODO: add endpoint to rerequest verification code
      no_longer_valid: "Dieser Verifizierungscode ist nicht mehr gültig.",
      too_many_attempts: "Zu viele falsche Versuche.",
      invalid_verification_code:
        "Der Verifizierunscode ist nicht korrekt. Bitte versuche es erneut.",
      email_exists: "Diese E-Mail-Adresse ist bereits in Verwendung.",
      default:
        "Beim Verifizieren ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    });
    return;
  }
  store.setAuthToken(resp.token);
  store.setRegisterVerifyState({
    registerVerifyEmail: "",
    registerVerifyUuid: "",
  });
  await store.checkStatus();
  toast.open({
    message: "Erfolgreich registriert!",
    type: "is-success",
  });
  router.push("/");
}

onMounted((): void => {
  if (store.isAuthenticated) {
    router.push("/");
  }
  if (!store.registerVerifyUuid) {
    router.push("/");
  }
  setTimeout(
    () => {
      showHelpText.value = true;
    },
    2 * 60 * 1000,
  );
});
</script>
