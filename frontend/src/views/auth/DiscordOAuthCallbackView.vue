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
import { DiscordAuthorizeResponse } from "@/types/oauth";

const route = useRoute();
const router = useRouter();
const store = useStore();
const toast = useToast();

onMounted(async () => {
  const err = route.query.error as string | undefined;
  if (err) {
    console.error("OAuth error: ", err);
    showErrorNotification(
      "Beim Verlinken mit Discord ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    );
    return;
  }
  const state = route.query.state as string;
  if (state !== sessionStorage.getItem("discordOAuthState")) {
    console.error("Invalid OAuth state!");
    showErrorNotification(
      "Beim Verlinken mit Discord ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    );
    return;
  }
  const code = route.query.code as string;
  const redirect_url = new URL(window.location.origin);
  redirect_url.pathname = router.resolve({
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

  store.setDiscordUsername(resp.username);
  toast.open({
    message: "Erfolgreich mit Discord verlinkt!",
    type: "is-success",
  });
  router.push("/");
});
</script>
