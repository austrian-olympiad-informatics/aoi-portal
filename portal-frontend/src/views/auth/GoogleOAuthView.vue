<template>
  <section>
    <h2 class="is-size-2">Redirecting...</h2>
  </section>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import oauth from "@/services/oauth";

@Component
export default class GoogleOAuthView extends Vue {
  async mounted() {
    const resp = await oauth.getGoogleAuthorizeURL();
    const url = new URL(resp.url);
    const array = new Uint8Array(16);
    window.crypto.getRandomValues(array);
    const state = [...array]
      .map((x) => x.toString(16).padStart(2, "0"))
      .join("");
    sessionStorage.setItem("googleOAuthState", state);
    url.searchParams.append("state", state);

    const redirect_url = new URL(window.location.origin);
    redirect_url.pathname = this.$router.resolve({
      name: "GoogleOAuthCallback",
    }).href;
    url.searchParams.append("redirect_uri", redirect_url.toString());

    // .replace to not affect browser history
    window.location.replace(url);
  }
}
</script>
