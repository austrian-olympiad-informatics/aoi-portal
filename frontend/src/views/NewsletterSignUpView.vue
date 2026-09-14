<template>
  <div class="container">
    <section class="section" v-if="!finished">
      <h1 class="title">Newsletter anmelden</h1>
      <form @submit.prevent="submit">
        <b-field label="E-Mail-Adresse">
          <b-input
            placeholder="Deine E-Mail-Adresse"
            type="email"
            icon="email"
            v-model="email"
            required
          >
          </b-input>
          <p class="control">
            <b-button
              type="is-primary"
              native-type="submit"
              label="Anmelden"
              :loading="loading"
            />
          </p>
        </b-field>
      </form>
    </section>
    <section class="section" v-else>
      <h1 class="title">Erfolgreich beim Newsletter angemeldet.</h1>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useToast } from "buefy";
import newsletter from "@/services/newsletter";
import { matchError } from "@/util/errors";

const toast = useToast();

const email = ref("");
const finished = ref(false);
const loading = ref(false);

async function submit() {
  loading.value = true;
  try {
    await newsletter.signUp({
      email: email.value,
    });
  } catch (err) {
    matchError(err, {
      default:
        "Beim Anmelden ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    });
    return;
  } finally {
    loading.value = false;
  }
  finished.value = true;
  toast.open({
    message: "Erfolgreich beim Newsletter angemeldet!",
    type: "is-success",
  });
}
</script>
