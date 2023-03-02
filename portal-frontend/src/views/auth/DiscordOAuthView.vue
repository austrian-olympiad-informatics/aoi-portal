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

@Component
export default class DiscordOAuthView extends Vue {
  async mounted() {
    const resp = await oauth.getDiscordAuthorizeURL();
    const url = new URL(resp.url);
    const array = new Uint8Array(16);
    window.crypto.getRandomValues(array);
    const state = [...array]
      .map((x) => x.toString(16).padStart(2, "0"))
      .join("");
    sessionStorage.setItem("discordOAuthState", state);
    url.searchParams.append("state", state);

    const redirect_url = new URL(window.location.origin);
    redirect_url.pathname = this.$router.resolve({
      name: "DiscordOAuthCallback",
    }).href;
    url.searchParams.append("redirect_uri", redirect_url.toString());

    // .replace to not affect browser history
    window.location.replace(url);
  }
}
</script>
