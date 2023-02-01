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
          loading="lazy"
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

      <b-field class="discord-tag" v-if="isDiscordLinked">
          <span class="icon">
              <img src="./../assets/discord-icon.svg" loading="lazy"/>
          </span>
          <b-tag class="username">{{ getDiscordUsername }}</b-tag>
      </b-field>

      <b-navbar-dropdown v-if="isAuthenticated">
        <template slot="label">
          <span class="icon-text ml-1">
            <b-icon class="mr-2" icon="account-circle" />
            <span>{{ name }}</span>
          </span>
        </template>
        <b-navbar-item tag="router-link" :to="{ name: 'Profile' }">
          <span class="icon-text">
            <b-icon class="mr-2" icon="account" />
            <span>Profil</span>
          </span>
        </b-navbar-item>
        <b-navbar-item v-if="isAdmin" tag="router-link" :to="isCMS ? { name: 'CMSAdminIndex' } : { name: 'AdminContests' }">
          <span class="icon-text">
            <b-icon class="mr-2" icon="cog" />
            <span>Admin</span>
          </span>
        </b-navbar-item>
        </b-navbar-item>
        <b-navbar-item @click="logout">
          <span class="icon-text">
            <b-icon class="mr-2" icon="logout" />
            <span>Abmelden</span>
          </span>
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
  get isAdmin(): boolean {
    return this.$store.getters.isAdmin;
  }
  get isCMS(): boolean {
    return this.$route.matched.some((x) => x.meta.isCMS);
  }
  get isAuthenticated(): boolean {
    return this.$store.getters.isAuthenticated;
  }
  get isNavbarSmall(): boolean {
    return this.$route.matched.some((x) => x.meta.navbarSmall);
  }
  get isDiscordLinked(): boolean {
    return !!this.$store.getters.discordUsername;
  }
  get getDiscordUsername(): string {
    return this.$store.getters.discordUsername;;
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
.aoi-logo {
  max-height: 48px !important;
  width: 48px;
  height: 48px;
}
.aoi-logo-text {
  padding-left: 0.5rem;
  font-size: 1.75rem !important;
  font-weight: 600 !important;
  font-family: "Arimo", sans-serif;
}
.navbar-container {
  border-bottom: 2px solid #f5f5f5;
}
.navbar {
  font-size: 1.125rem;
  min-height: initial !important;
}

.discord-tag {
  position: relative;
  top: 20px;
}

.discord-tag .username {
  margin-left: 5px;
}

@media screen and (max-width: 768px) {
  .aoi-logo-text {
    font-size: 1.35rem !important;
  }
}
</style>

<style>
.navbar-burger {
  margin-top: 0.5rem !important;
  margin-right: 0.75rem !important;
  margin-left: auto !important;
}
</style>
