<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="is-size-2 mb-3">Passwort vergessen</h1>
      <b-field label="E-Mail-Adresse">
        <b-input
          v-model="email"
          type="email"
          placeholder="z.B. alice@gmail.com"
          required
        />
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded class="mt-5"
        >Weiter</b-button
      >
    </form>
  </center-box-layout>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

@Component({
  components: {
    CenterBoxLayout,
  },
})
export default class PasswordResetView extends Vue {
  email: string = "";

  async submit() {
    const resp = await auth.requestPasswordReset({
      email: this.email,
    });
    this.$store.commit("setPasswordResetVerifyState", {
      passwordResetVerifyEmail: this.email,
      passwordResetVerifyUuid: resp.uuid,
    });
    this.$router.push({ name: "PasswordResetVerify" });
  }
}
</script>
