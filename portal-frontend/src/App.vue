<template>
  <div id="app">
    <div class="navbar-container">
      <nav class="navbar" role="navigation" aria-label="main navigation">
        <div class="navbar-brand">
          <a class="navbar-item aoi-logo-container">
            <img
              alt="Informatikolympiade Logo"
              src="./assets/logo.jpg"
              class="aoi-logo"
            />
            <span class="aoi-logo-text">Informatikolympiade</span>
          </a>
        </div>

        <div class="navbar-menu">
          <!-- <div class="navbar-start">
          <a class="navbar-item"> Home </a>

          <a class="navbar-item"> Documentation </a>

          <div class="navbar-item has-dropdown is-hoverable">
            <a class="navbar-link"> More </a>

            <div class="navbar-dropdown">
              <a class="navbar-item"> About </a>
              <a class="navbar-item"> Jobs </a>
              <a class="navbar-item"> Contact </a>
              <hr class="navbar-divider" />
              <a class="navbar-item"> Report an issue </a>
            </div>
          </div>
        </div> -->

          <div class="navbar-end">
            <div class="navbar-item">
              <div class="buttons">
                <b-button type="is-primary"
                  ><strong>Registrieren</strong></b-button
                >
                <b-button type="is-light">Anmelden</b-button>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </div>

    <section class="section">
      <router-view />
    </section>

    <footer class="footer">
      <div class="content container is-max-desktop has-text-centered">
        <p>&copy; Österreichische Informatikolympiade 2022</p>
      </div>
    </footer>
    <b-button
      class="admin-button"
      v-if="isAdmin"
      type="is-danger"
      tag="router-link"
      to="/admin"
      icon-right="cog"
    />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class AppComponent extends Vue {
  get isAdmin(): boolean {
    return true;
  }
}
</script>

<style scoped>
.aoi-logo-container {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
.aoi-logo {
  max-height: 48px !important;
  width: 48px;
  height: 48px;
}
.aoi-logo-text {
  padding-left: 0.5rem;
  font-size: 1.5rem !important;
  font-weight: 420;
}
.navbar {
  font-size: 1.125rem;
  padding: 1.5rem 0;
  max-width: 900px;
  flex-grow: 1;
  margin: 0 auto;
  width: auto;
}
.navbar-container {
  border-bottom: 2px solid #f5f5f5;
}
#app {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
}
.section {
  flex: 1;
  margin: 0 auto;
  width: 900px;
  max-width: 900px;
}
.footer {
  padding: 1.5rem 1rem 1.5rem !important;
}
.admin-button {
  position: fixed;
  right: 60px;
  bottom: 40px;
  opacity: 0.8;
}
</style>
