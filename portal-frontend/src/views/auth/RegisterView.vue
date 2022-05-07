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
import { NotificationProgrammatic as Notification } from "buefy";
import { AxiosError } from "axios";

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

    try {
      const resp = await auth.register({
        first_name: this.data.first_name,
        last_name: this.data.last_name,
        email: this.data.email,
        password: this.data.password,
      });

      this.$store.commit("setRegisterVerifyState", {
        registerVerifyEmail: this.data.email,
        registerVerifyUuid: resp.uuid,
      });

      this.$router.push({ name: "RegisterVerify" });
    } catch(error) {
      const err = error as AxiosError;

      if(err.response?.status == 409)
      {
          Notification.open({
          message: "Diese E-Mail-Adresse ist bereits in Verwendung.",
          type: "is-danger",
          hasIcon: true,
          position: "is-top-right",
        });
      }
      else
      {
        Notification.open({
          message: "Beim Registrieren ist etwas schiefgelaufen. Bitte versuche es später erneut.",
          type: "is-danger",
          hasIcon: true,
          position: "is-top-right",
        });
      }
    }
    
  }
  mounted(): void {
    if (this.$store.getters.isAuthenticated) {
      this.$router.push("/");
    }
  }
}
</script>
