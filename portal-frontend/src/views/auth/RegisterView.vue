<template>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-5">
          <form class="box" @submit.prevent="register">
            <h1 class="is-size-2 mb-3">Registrieren</h1>
            <RegisterInput v-model="data" />
            <b-button type="is-primary" native-type="submit" expanded
              >Registrieren</b-button
            >

            <p class="mt-5">
              <router-link :to="{ name: 'Login' }">Zur Anmeldung</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";
import RegisterInput, {
  RegisterInputData,
} from "@/components/RegisterInput.vue";
import { AuthRegisterResult } from "@/types/auth";
import { matchError } from "@/util/errors";

@Component({
  components: {
    RegisterInput,
  },
})
export default class RegisterView extends Vue {
  data: RegisterInputData = {
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  };

  async register() {
    let resp: AuthRegisterResult;

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
