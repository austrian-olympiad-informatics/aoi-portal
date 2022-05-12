<template>
  <div>
    <HomeHero v-if="!isAuthenticated" />
    <HomeContests v-if="isAuthenticated" />>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import HomeHero from "@/components/HomeHero.vue";
import HomeContests from "@/components/HomeContests.vue";

@Component({
  components: {
    HomeHero,
    HomeContests,
  },
})
export default class HomeView extends Vue {
  get isAuthenticated(): boolean {
    return this.$store.getters.isAuthenticated;
  }
}
</script>
