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
import { DiscordAuthorizeResponse } from "@/types/oauth";

@Component
export default class DiscordOAuthCallbackView extends Vue {
  async mounted() {
    const err = this.$route.query.error as string | undefined;
    if (err) {
      console.error("OAuth error: ", err);
      showErrorNotification(
        "Beim Verlinken mit Discord ist etwas schiefgelaufen. Bitte versuche es später erneut."
      );
      return;
    }
    const state = this.$route.query.state as string;
    if (state !== sessionStorage.getItem("discordOAuthState")) {
      console.error("Invalid OAuth state!");
      showErrorNotification(
        "Beim Verlinken mit Discord ist etwas schiefgelaufen. Bitte versuche es später erneut."
      );
      return;
    }
    const code = this.$route.query.code as string;
    const redirect_url = new URL(window.location.origin);
    redirect_url.pathname = this.$router.resolve({
      name: "DiscordOAuthCallback",
    }).href;

    let resp: DiscordAuthorizeResponse;
    try {
      resp = await oauth.discordAuthorize({
        code: code,
        redirect_uri: redirect_url.toString(),
      });
    } catch (err) {
      matchError(err, {
        default:
          "Beim Verlinken mit Discord ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    }

    this.$store.commit("setDiscordUsername", resp.username);
    this.$buefy.toast.open({
      message: "Erfolgreich mit Discord verlinkt!",
      type: "is-success",
    });
    this.$router.push("/");
  }
}
</script>
