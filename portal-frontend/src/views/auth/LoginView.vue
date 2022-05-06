<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-5">
          <LoginForm @logged-in="loggedIn" />
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import LoginForm from "@/components/LoginForm.vue";

@Component({
  components: {
    LoginForm,
  },
})
export default class LoginView extends Vue {
  loggedIn(): void {
    this.$buefy.toast.open({
      message: "Erfolgreich angemeldet!",
      type: "is-success",
    });
    this.$router.push("/");
  }
  mounted(): void {
    if (this.$store.getters.isAuthenticated) {
      this.$router.push("/");
    }
  }
}
</script>
