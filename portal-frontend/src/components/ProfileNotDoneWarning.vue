<template>
  <b-message type="is-warning" has-icon v-if="!profileComplete">
    Dein Profil ist noch nicht fertig ausgefüllt. Damit du dich für
    Trainingscamps und den Bundesbewerb qualifieren kannst, musst du diese in
    den
    <router-link :to="{ name: 'Profile' }">Profileinstellungen</router-link>
    ausfüllen.
    <b-button
      tag="router-link"
      icon-right="chevron-right"
      :to="{ name: 'Profile' }"
      class="is-pulled-right"
      type="is-text"
      >Zu den Profileinstellungen</b-button
    >
  </b-message>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import profile from "@/services/profile";
import { ProfileInfoResponse } from "@/types/profile";

@Component
export default class ProfileNotDoneWarning extends Vue {
  profile: ProfileInfoResponse | null = null;

  get profileComplete(): boolean {
    if (this.profile === null) return true;
    return !!(
      this.profile.first_name &&
      this.profile.last_name &&
      this.profile.birthday &&
      this.profile.phone_nr &&
      this.profile.address_street &&
      this.profile.address_zip &&
      this.profile.address_town &&
      this.profile.school_name &&
      this.profile.school_address
    );
  }

  async loadProfile() {
    this.profile = await profile.profileInfo();
  }
  async mounted() {
    await this.loadProfile();
  }
}
</script>
