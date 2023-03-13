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

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class AdminCard extends Vue {
  @Prop({
    type: Boolean,
    default: false,
  })
  loading!: boolean;
}
</script>
