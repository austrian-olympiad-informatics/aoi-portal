<template>
  <div class="container">
    <section class="section">
      <div class="columns is-centered">
        <div class="column is-8-tablet is-8-desktop is-6-widescreen">
          <div class="box">
            <slot></slot>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class CenterBoxLayout extends Vue {}
</script>
