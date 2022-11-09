<template>
  <center-box-layout>
    <form @submit.prevent="register">
      <h1 class="title is-3 mb-3">Registrieren</h1>
      <b-message type="is-info">
        <small>
          Hinweis: Du kannst dich hier auch als Lehrer:in oder Externe:r registrieren
          (für Trainigsaufgaben etc). Die Anmeldung für die Qualifikationsrunde
          erfolgt in einem nächsten Schritt.
        </small>
      </b-message>
      <RegisterInput v-model="data" />
      <b-button
        class="mt-3"
        type="is-primary"
        native-type="submit"
        expanded
        :loading="submitButtonLoading"
        >Registrieren</b-button
      >
    </form>

    <p class="mt-5">
      <router-link :to="{ name: 'Login' }">Zur Anmeldung</router-link>
    </p>
    <div class="is-divider" data-content="ODER"></div>
    <router-link
      class="button is-rounded is-fullwidth"
      type="button"
      :to="{ name: 'GitHubOAuth' }"
    >
      <span class="icon">
        <img src="../../assets/github-icon.svg" loading="lazy" />
      </span>
      Mit GitHub registrieren
    </router-link>
    <router-link
      class="button is-rounded is-fullwidth mt-2"
      type="button"
      :to="{ name: 'GoogleOAuth' }"
    >
      <span class="icon">
        <img src="../../assets/google-icon.svg" loading="lazy" />
      </span>
      Mit Google registrieren
    </router-link>
  </center-box-layout>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";
import RegisterInput, {
  RegisterInputData,
} from "@/components/RegisterInput.vue";
import { AuthRegisterResult } from "@/types/auth";
import { matchError } from "@/util/errors";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

@Component({
  components: {
    RegisterInput,
    CenterBoxLayout,
  },
})
export default class RegisterView extends Vue {
  data: RegisterInputData = {
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  };
  submitButtonLoading = false;

  async register() {
    let resp: AuthRegisterResult;

    this.submitButtonLoading = true;
    try {
      resp = await auth.register({
        first_name: this.data.first_name,
        last_name: this.data.last_name,
        email: this.data.email,
        password: this.data.password,
      });
    } catch (error) {
      matchError(error, {
        email_exists: "Diese E-Mail-Adresse ist bereits in Verwendung.",
        rate_limit: "Zu viele Registrierversuche für diese E-Mail-Adresse.",
        default:
          "Beim Registrieren ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    } finally {
      this.submitButtonLoading = false;
    }

    this.$store.commit("setRegisterVerifyState", {
      registerVerifyEmail: this.data.email,
      registerVerifyUuid: resp.uuid,
    });

    this.$router.push({ name: "RegisterVerify" });
  }
  mounted(): void {
    if (this.$store.getters.isAuthenticated) {
      this.$router.push("/");
    }
  }
}
</script>

<style scoped>
.is-divider {
  display: block;
  position: relative;
  border-top: 0.1rem solid #dbdbdb;
  height: 0.1rem;
  margin: 2rem 0;
  text-align: center;
}
.is-divider::after {
  background: #fff;
  color: #b5b5b5;
  content: attr(data-content);
  display: inline-block;
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
  transform: translateY(-1.1rem);
  text-align: center;
}

.button .icon {
  margin-right: 0.5em !important;
}
.button .icon img {
  height: 1.5em;
  display: inline-block;
}
</style>
