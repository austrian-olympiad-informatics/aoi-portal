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
import { GoogleAuthorizeResponse } from "@/types/oauth";

@Component
export default class GoogleOAuthCallbackView extends Vue {
  async mounted() {
    const err = this.$route.query.error as string | undefined;
    if (err) {
      console.error("OAuth error: ", err);
      showErrorNotification(
        "Beim Anmelden mit Google ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      );
      return;
    }
    const state = this.$route.query.state as string;
    if (state !== sessionStorage.getItem("googleOAuthState")) {
      console.error("Invalid OAuth state!");
      showErrorNotification(
        "Beim Anmelden mit Google ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      );
      return;
    }
    const code = this.$route.query.code as string;
    const redirect_url = new URL(window.location.origin);
    redirect_url.pathname = this.$router.resolve({
      name: "GoogleOAuthCallback",
    }).href;

    let resp: GoogleAuthorizeResponse;
    try {
      resp = await oauth.googleAuthorize({
        code: code,
        redirect_uri: redirect_url.toString(),
      });
    } catch (err) {
      matchError(err, {
        default:
          "Beim Anmelden mit Google ist etwas schiefgelaufen. Bitte versuche es später erneut.",
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
