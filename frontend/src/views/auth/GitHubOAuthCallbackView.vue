<template>
  <div class="container">
    <div class="section">
      <h2 class="title is-3">Redirecting...</h2>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import oauth from "@/services/oauth";
import { matchError, showErrorNotification } from "@/util/errors";
import { GitHubAuthorizeResponse } from "@/types/oauth";

@Component
export default class GitHubOAuthCallbackView extends Vue {
  async mounted() {
    const err = this.$route.query.error as string | undefined;
    if (err) {
      console.error("OAuth error: ", err);
      showErrorNotification(
        "Beim Anmelden mit GitHub ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      );
      return;
    }
    const state = this.$route.query.state as string;
    if (state !== sessionStorage.getItem("githubOAuthState")) {
      console.error("Invalid OAuth state!");
      showErrorNotification(
        "Beim Anmelden mit GitHub ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      );
      return;
    }
    const code = this.$route.query.code as string;
    let resp: GitHubAuthorizeResponse;
    try {
      resp = await oauth.githubAuthorize({
        code: code,
      });
    } catch (err) {
      matchError(err, {
        default:
          "Beim Anmelden mit GitHub ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    }

    this.$store.commit("setAuthToken", resp.token);
    await this.$store.dispatch("checkStatus");
    this.$buefy.toast.open({
      message: "Erfolgreich angemeldet!",
      type: "is-success",
    });
    this.$router.push("/");
  }
}
</script>
