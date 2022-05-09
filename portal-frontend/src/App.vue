<template>
  <div id="app">
    <Navbar />

    <section>
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
      :to="{ name: 'AdminIndex' }"
      icon-right="cog">
      Admin
    </b-button>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Navbar from "./components/Navbar.vue";
import { NotificationProgrammatic as Notification } from "buefy";

@Component({
  components: {
    Navbar,
  },
})
export default class AppComponent extends Vue {
  get isAdmin(): boolean {
    return this.$store.getters.isAdmin;
  }
  async mounted(): Promise<void> {
    try {
      await this.$store.dispatch("checkStatus");
    } catch(except) {
      Notification.open({
          message: "Beim Anmelden ist etwas schiefgelaufen. Bitte versuche es später erneut.",
          type: "is-danger",
          hasIcon: true,
          position: "is-top-right",
      });
    }
  }
}
</script>

<style scoped>
#app {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  /*background-color: #fbfbfb;*/
}
section {
  flex: 1;
}
footer {
  padding: 2rem 1.5rem 2rem;
  /*background-color: #f3f3f3;*/
}
.admin-button {
  position: fixed;
  right: 60px;
  bottom: 40px;
  opacity: 0.8;
}
</style>
