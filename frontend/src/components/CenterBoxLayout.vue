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
import {  Component, Vue, toNative } from "vue-facing-decorator";

@Component
class CenterBoxLayout extends Vue {}
export default toNative(CenterBoxLayout)
</script>
