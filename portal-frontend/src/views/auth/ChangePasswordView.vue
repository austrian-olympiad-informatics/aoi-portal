<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="is-size-2 mb-3">Passwort ändern</h1>
      <b-field label="Aktuelles Passwort">
        <b-input
          v-model="currentPassword"
          type="password"
          placeholder="Aktuelles Passwort"
          required
        />
      </b-field>
      <b-field label="Neues Passwort festlegen">
        <b-input
          v-model="newPassword"
          type="password"
          placeholder="********"
          minlength="8"
          required
        />
      </b-field>
      <b-field
        label="Neues Passwort bestätigen"
        :type="{ 'is-danger': !newPasswordsMatch }"
        :message="{
          'Passwörter müssen übereinstimmen': !newPasswordsMatch,
        }"
      >
        <b-input
          v-model="newPasswordConfirm"
          type="password"
          placeholder="********"
          minlength="8"
          required
        />
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded class="mt-5"
        >Speichern</b-button
      >
    </form>
  </center-box-layout>
</template>

<script lang="ts">
import auth from "@/services/auth";
import { Component, Vue } from "vue-property-decorator";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";
import { matchError } from "@/util/errors";

@Component({
  components: {
    CenterBoxLayout,
  },
})
export default class ChangePasswordView extends Vue {
  currentPassword: string = "";
  newPassword: string = "";
  newPasswordConfirm: string = "";

  get newPasswordsMatch(): boolean {
    return this.newPassword === this.newPasswordConfirm;
  }

  async submit() {
    if (!this.newPasswordsMatch) return;
    try {
      await auth.changePassword({
        old_password: this.currentPassword,
        new_password: this.newPassword,
      });
    } catch (err) {
      matchError(err, {
        invalid_password: "Das aktuelle Passwort ist inkorrekt.",
        default: "Beim Passwort Ändern ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    }

    this.$buefy.toast.open({
      message: "Passwort geändert!",
      type: "is-success",
    });
    this.$router.push({ name: "Profile" });
  }
}
</script>
