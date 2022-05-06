<template>
  <div>
    <div v-if="!isAuthenticated" class="hero is-fullheight-with-navbar">
      <div class="hero-body">
        <div class="welcome container has-text-centered">
          <img
            alt="Informatikolympiade Logo"
            src="@/assets/logo-big.png"
            class="aoi-logo"
          />
          <h1 class="title">Österreichische Informatikolympiade</h1>
          <h2 class="subtitle">
            Melde dich an, um Trainingsaufgaben zu lösen und an
            Qualifikationsrunden teilzunehmen.
          </h2>

          <div class="buttons">
            <b-button
              type="is-primary is-large"
              tag="router-link"
              :to="{ name: 'Register' }"
              ><strong>Registrieren</strong></b-button
            >
            <b-button
              type="is-light is-large"
              tag="router-link"
              :to="{ name: 'Login' }"
              >Anmelden</b-button
            >
          </div>
        </div>
      </div>
    </div>

    <div v-if="isAuthenticated" class="container">
      <section class="section">
        <profile-not-done-warning />
        <h1 class="title">Wettbewerbe</h1>
        <div class="block">
          <p>Hier kannst du dich bei unseren Wettbewerbsservern anmelden.</p>
        </div>
        <contests-grid />
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import ContestsGrid from "@/components/ContestsGrid.vue";
import { Component, Vue } from "vue-property-decorator";
import ProfileNotDoneWarning from "@/components/ProfileNotDoneWarning.vue";

@Component({
  components: {
    ContestsGrid,
    ProfileNotDoneWarning,
  },
})
export default class HomeView extends Vue {
  get isAuthenticated(): boolean {
    return this.$store.getters.isAuthenticated;
  }
}
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
