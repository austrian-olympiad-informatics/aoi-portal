<template>
  <b-navbar shadow>
    <template #brand>
      <b-navbar-item tag="router-link" :to="{ path: '/' }">
        <img
          alt="Informatikolympiade Logo"
          src="@/assets/logo.png"
          class="aoi-logo"
          width="48"
          height="48"
        />
        <span class="aoi-logo-text">Informatikolympiade</span>
      </b-navbar-item>
    </template>
    <template #start> </template>

    <template #end>
      <b-navbar-item
        v-if="!isAuthenticated && !$route.meta.noNavAuth"
        tag="div"
      >
        <div class="buttons">
          <b-button
            type="is-primary"
            tag="router-link"
            :to="{ name: 'Register' }"
            ><strong>Registrieren</strong></b-button
          >
          <b-button type="is-light" tag="router-link" :to="{ name: 'Login' }"
            >Anmelden</b-button
          >
        </div>
      </b-navbar-item>

      <b-navbar-dropdown v-if="isAuthenticated">
        <template slot="label">
          <b-icon class="ml-1 mr-2" icon="account-circle" /> {{ name }}
        </template>
        <b-navbar-item tag="router-link" :to="{ name: 'Profile' }">
          <b-icon class="mr-2" icon="account" /> Profil
        </b-navbar-item>
        <b-navbar-item @click="logout">
          <b-icon class="mr-2" icon="logout" /> Abmelden
        </b-navbar-item>
      </b-navbar-dropdown>
    </template>
  </b-navbar>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Navbar extends Vue {
  get isAuthenticated(): boolean {
    return this.$store.getters.isAuthenticated;
  }

  get name(): string {
    return `${this.$store.getters.firstName} ${this.$store.getters.lastName}`;
  }
  async logout(): Promise<void> {
    await auth.logout();
    this.$store.commit("setAuthToken", "");
    this.$store.dispatch("checkStatus");
    this.$router.push("/");
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
  padding: 1.5rem 1rem;
  font-size: 1.125rem;
}
.navbar-container {
  border-bottom: 2px solid #f5f5f5;
}
</style>
