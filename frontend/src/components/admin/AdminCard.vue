<template>
  <div>
    <p class="title is-3">
      <slot name="title"></slot>
    </p>

    <div v-if="loading">
      <b-skeleton width="20%" animated></b-skeleton>
      <b-skeleton width="40%" animated></b-skeleton>
      <b-skeleton width="80%" animated></b-skeleton>
      <b-skeleton animated></b-skeleton>
    </div>
    <slot v-if="!loading"></slot>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ loading?: boolean }>(), { loading: false });
</script>
