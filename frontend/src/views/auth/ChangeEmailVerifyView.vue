<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-5">
          <form class="box" @submit.prevent="changeEmailVerify">
            <h1 class="title is-3 mb-3">Wir haben dir einen Code gesendet</h1>
            <p>Gib ihn unten zur Verifizierung von {{ newMail }} ein.</p>
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
import { matchError } from "@/util/errors";

const router = useRouter();
const store = useStore();
const toast = useToast();

const verifyCode = ref("");

const newMail = computed(() => store.changeEmailVerifyEmail);

async function changeEmailVerify() {
  try {
    await auth.changeEmailVerify({
      uuid: store.changeEmailVerifyUuid,
      verification_code: verifyCode.value,
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

  store.setChangeEmailVerifyState({
    changeEmailVerifyEmail: "",
    changeEmailVerifyUuid: "",
  });
  await store.checkStatus();
  toast.open({
    message: "E-Mail-Adresse erfolgreich geändert!",
    type: "is-success",
  });
  router.push("/");
}

onMounted((): void => {
  if (!store.changeEmailVerifyUuid) {
    router.push("/");
  }
});
</script>
