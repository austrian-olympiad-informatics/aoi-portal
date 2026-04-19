<template>
  <div>
    <Navbar />

    <section>
      <router-view />
    </section>

    <footer class="footer" v-if="!isFooterHidden">
      <div class="content container is-max-desktop has-text-centered">
        <p>&copy; Österreichische Informatikolympiade 2026</p>
      </div>
    </footer>

    <b-button
      class="discord-button"
      type="is-link"
      v-if="isAuthenticated && !isProxyAuth && !isDiscordButtonHidden && !isDiscordLinked"
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
      v-if="isAdmin && !isProxyAuth && !isAdminButtonHidden"
      type="is-danger"
      tag="router-link"
      :to="isCMS ? { name: 'CMSAdminIndex' } : { name: 'AdminContests' }"
      icon-right="cog"
    >
      Admin
    </b-button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useStore } from "@/store";
import Navbar from "./components/Navbar.vue";

const store = useStore();
const route = useRoute();

const isAdmin = computed(() => store.isAdmin);
const isAuthenticated = computed(() => store.isAuthenticated);
const isProxyAuth = computed(() => store.isProxyAuth);
const isDiscordLinked = computed(() => !!store.discordUsername);
const isFooterHidden = computed(() =>
  route.matched.some((x) => x.meta.footerHidden),
);
const isCMS = computed(() => route.matched.some((x) => x.meta.isCMS));
const isAdminButtonHidden = computed(() =>
  route.matched.some((x) => x.meta.isAdminButtonHidden),
);
const isDiscordButtonHidden = computed(() =>
  route.matched.some((x) => x.meta.isDiscordButtonHidden),
);

onMounted(async () => {
  await store.checkStatus();
});
</script>

<style>
html,
body {
  height: 100%;
}
#app {
  display: flex;
  min-height: -webkit-fill-available;
  height: 100%;
  flex-direction: column;
}
#app > * {
  display: flex;
  flex-direction: column;
  flex: 1 0 auto;
  min-height: 0;
}
</style>

<style scoped>
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
