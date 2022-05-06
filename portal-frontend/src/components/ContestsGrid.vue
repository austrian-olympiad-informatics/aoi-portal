<template>
  <div class="contests-container">
    <div v-for="contest in contests" :key="contest.uuid">
      <contest-card :contest="contest" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import contests from "@/services/contests";
import { Contests } from "@/types/contests";
import ContestCard from "./ContestCard.vue";

@Component({
  components: {
    ContestCard,
  },
})
export default class ContestsGrid extends Vue {
  contests: Contests | null = null;

  async loadContests() {
    this.contests = await contests.listContests();
  }

  async mounted() {
    await this.loadContests();
  }
}
</script>

<style scoped>
.contests-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
</style>
