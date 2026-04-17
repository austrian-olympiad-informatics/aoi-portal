<template>
  <div>
    <div class="hero is-fullheight-with-navbar">
      <div class="hero-body">
        <div class="welcome container has-text-centered">
          <img
            alt="Informatikolympiade Logo"
            src="@/assets/logo-big.png"
            class="aoi-logo"
            loading="lazy"
          />
          <h1 class="title">Oooops. Da ist was schiefgelaufen.</h1>
          <h2 class="subtitle">
            Es ist ein Fehler aufgetreten. Bitte versuche es später erneut!
          </h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {  Component, Vue, toNative } from "vue-facing-decorator";

@Component({
  components: {},
})
class ErrorView extends Vue {}
export default toNative(ErrorView)
</script>

<style scoped>
.hero {
  /*min-height: calc(100vh - 6.5rem) !important;*/
  min-height: calc(100vh - 12.5rem) !important;
}
.aoi-logo {
  width: 250px;
  margin-bottom: 20px;
}
.welcome h1 {
  font-weight: 600;
  font-size: 4rem;
  margin-bottom: 2rem;
}
.welcome h2 {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}
</style>
