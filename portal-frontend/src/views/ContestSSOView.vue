<template>
  <section>
    <h2 class="is-size-2">Redirecting...</h2>
  </section>
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
