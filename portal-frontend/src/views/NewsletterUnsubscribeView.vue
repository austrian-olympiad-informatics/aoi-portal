<template>
  <div class="container">
    <section class="section" v-if="!finished">
      <h1 class="title"></h1>
    </section>
    <section class="section" v-else>
      <h1 class="title">Sie wurden vom Newsletter abgemeldet.</h1>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import newsletter from "@/services/newsletter";
import { matchError } from "@/util/errors";

@Component
export default class NewsletterUnsubscribeView extends Vue {
  finished = false;

  async mounted() {
    const email = this.$route.query.email;
    const token = this.$route.query.token;
    try {
      await newsletter.unsubscribe({
        email: email as string,
        token: token as string,
      });
    } catch (err) {
      matchError(err, {
        default:
          "Beim Abbestellen ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    }
    this.$buefy.toast.open({
      message: "Erfolgreich vom Newsletter abgemeldet!",
      type: "is-success",
    });
    this.finished = true;
  }
}
</script>
