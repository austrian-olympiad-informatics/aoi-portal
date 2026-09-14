<template>
  <div class="container">
    <div class="section">
      <h2 class="title is-3">Redirecting...</h2>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useStore } from "@/store";
import { useToast } from "buefy";
import oauth from "@/services/oauth";
import { matchError, showErrorNotification } from "@/util/errors";
import { GitHubAuthorizeResponse } from "@/types/oauth";

const route = useRoute();
const router = useRouter();
const store = useStore();
const toast = useToast();

onMounted(async () => {
  const err = route.query.error as string | undefined;
  if (err) {
    console.error("OAuth error: ", err);
    showErrorNotification(
      "Beim Anmelden mit GitHub ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    );
    return;
  }
  const state = route.query.state as string;
  if (state !== sessionStorage.getItem("githubOAuthState")) {
    console.error("Invalid OAuth state!");
    showErrorNotification(
      "Beim Anmelden mit GitHub ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    );
    return;
  }
  const code = route.query.code as string;
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

  store.setAuthToken(resp.token);
  await store.checkStatus();
  toast.open({
    message: "Erfolgreich angemeldet!",
    type: "is-success",
  });
  router.push("/");
});
</script>
