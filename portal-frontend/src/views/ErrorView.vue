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
import { Component, Vue } from "vue-property-decorator";

@Component({
  components: {},
})
export default class ErrorView extends Vue {}
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
.welcome .buttons {
  justify-content: center;
}
.welcome .buttons .button:not(:last-child) {
  margin-right: 1.5rem;
}
</style>
