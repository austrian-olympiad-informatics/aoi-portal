<template>
  <div class="container">
    <div class="section">
      <h2 class="title is-3">Redirecting...</h2>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import contests from "@/services/contests";

@Component
export default class ContestSSOView extends Vue {
  async mounted() {
    const contestUuid = this.$route.params.contestUuid;
    const resp = await contests.genSSOToken(contestUuid);
    const url = new URL(resp.endpoint);
    url.searchParams.append("token", resp.token);
    // .replace to not affect browser history
    window.location.replace(url);
  }
}
</script>
