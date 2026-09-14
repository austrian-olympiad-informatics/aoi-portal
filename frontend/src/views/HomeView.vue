<template>
  <div>
    <HomeHero v-if="!isAuthenticated" />
    <HomeContests v-if="isAuthenticated" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useStore } from "@/store";
import HomeHero from "@/components/HomeHero.vue";
import HomeContests from "@/components/HomeContests.vue";

const store = useStore();
const isAuthenticated = computed(() => store.isAuthenticated);
</script>
