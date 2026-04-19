<template>
  <div class="container">
    <div class="section">
      <h2 class="title is-3">Redirecting...</h2>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import contests from "@/services/contests";

const route = useRoute();

onMounted(async () => {
  const contestUuid = route.params.contestUuid as string;
  const resp = await contests.genSSOToken(contestUuid);
  const url = new URL(resp.endpoint);
  url.searchParams.append("token", resp.token);
  // .replace to not affect browser history
  window.location.replace(url);
});
</script>
