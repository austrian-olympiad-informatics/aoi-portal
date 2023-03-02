<template>
  <div id="app">
    <Navbar />

    <section>
      <router-view />
    </section>

    <footer class="footer" v-if="!isFooterHidden">
      <div class="content container is-max-desktop has-text-centered">
        <p>&copy; Österreichische Informatikolympiade 2022</p>
      </div>
    </footer>

    <b-button
      class="discord-button"
      type="is-link"
      v-if="isAuthenticated && !isDiscordButtonHidden && !isDiscordLinked"
      tag="router-link"
      :to="{ name: 'DiscordOAuth' }"
    >
      <span class="icon">
        <img src="./assets/discord-icon-white.svg" loading="lazy" />
      </span>
      <span> Mit Discord verbinden </span>
    </b-button>

    <b-button
      class="admin-button"
      v-if="isAdmin && !isAdminButtonHidden"
      type="is-danger"
      tag="router-link"
      :to="isCMS ? { name: 'CMSAdminIndex' } : { name: 'AdminContests' }"
      icon-right="cog"
    >
      Admin
    </b-button>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Navbar from "./components/Navbar.vue";

@Component({
  components: {
    Navbar,
  },
})
export default class AppComponent extends Vue {
  get isAdmin(): boolean {
    return this.$store.getters.isAdmin;
  }
  get isFooterHidden(): boolean {
    return this.$route.matched.some((x) => x.meta.footerHidden);
  }
  get isCMS(): boolean {
    return this.$route.matched.some((x) => x.meta.isCMS);
  }
  get isAdminButtonHidden(): boolean {
    return this.$route.matched.some((x) => x.meta.isAdminButtonHidden);
  }
  get isDiscordButtonHidden(): boolean {
    return this.$route.matched.some((x) => x.meta.isDiscordButtonHidden);
  }
  get isAuthenticated(): boolean {
    return this.$store.getters.isAuthenticated;
  }
  get isDiscordLinked(): boolean {
    return !!this.$store.getters.discordUsername;
  }
  get getDiscordUsername(): string {
    return this.$store.getters.discordUsername;
  }
  async mounted(): Promise<void> {
    await this.$store.dispatch("checkStatus");
  }
}
</script>

<style>
html,
body {
  height: 100%;
}
</style>

<style scoped>
#app {
  display: flex;
  min-height: -webkit-fill-available;
  height: 100%;
  flex-direction: column;
}
section {
  flex: 1 0 auto;
}
footer {
  padding: 2rem 1.5rem 2rem;
  flex-shrink: 0;
}
.admin-button {
  position: fixed;
  right: 60px;
  bottom: 40px;
  opacity: 0.8;
}

.discord-tag {
  position: fixed;
  right: 180px;
  bottom: 40px;
  opacity: 1;
}

.discord-button {
  position: fixed;
  right: 180px;
  bottom: 40px;
  opacity: 1;
}

.discord-button span {
  vertical-align: middle;
  display: inline-block;
}

.button .icon {
  margin-right: 0.5em !important;
  vertical-align: middle;
}
.button .icon img {
  height: 1.5em;
  display: inline-block;
}
</style>
