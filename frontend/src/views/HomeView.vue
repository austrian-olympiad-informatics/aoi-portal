<template>
  <div>
    <HomeHero v-if="!isAuthenticated" />
    <HomeContests v-if="isAuthenticated" />
  </div>
</template>

<script lang="ts">
import {  Component, Vue, toNative } from "vue-facing-decorator";
import { useStore } from "@/store";
import HomeHero from "@/components/HomeHero.vue";
import HomeContests from "@/components/HomeContests.vue";

@Component({
  components: {
    HomeHero,
    HomeContests,
  },
})
class HomeView extends Vue {
  get isAuthenticated(): boolean {
    return useStore().isAuthenticated;
  }
}
export default toNative(HomeView)
</script>
