<template>
  <div class="container">
    <div class="section">
      <h2 class="title is-3">Redirecting...</h2>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import oauth from "@/services/oauth";

const router = useRouter();

onMounted(async () => {
  const resp = await oauth.getGithubAuthorizeURL();
  const url = new URL(resp.url);
  const array = new Uint8Array(16);
  window.crypto.getRandomValues(array);
  const state = [...array]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
  sessionStorage.setItem("githubOAuthState", state);
  url.searchParams.append("state", state);

  const redirect_url = new URL(window.location.origin);
  redirect_url.pathname = router.resolve({
    name: "GitHubOAuthCallback",
  }).href;
  url.searchParams.append("redirect_uri", redirect_url.toString());

  // .replace to not affect browser history
  window.location.replace(url);
});
</script>
