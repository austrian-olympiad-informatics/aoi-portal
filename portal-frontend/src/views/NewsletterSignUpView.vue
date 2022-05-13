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

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import newsletter from "@/services/newsletter";
import { matchError } from "@/util/errors";

@Component
export default class NewsletterSignUpView extends Vue {
  email = "";
  finished = false;
  loading = false;

  async submit() {
    this.loading = true;
    try {
      await newsletter.signUp({
        email: this.email,
      });
    } catch (err) {
      matchError(err, {
        default:
          "Beim Anmelden ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    } finally {
      this.loading = false;
    }
    this.finished = true;
    this.$buefy.toast.open({
      message: "Erfolgreich beim Newsletter angemeldet!",
      type: "is-success",
    });
  }
}
</script>
