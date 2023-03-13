<template>
  <div class="container">
    <section class="section">
      <div v-if="(profile === null || contests === null) && showLoading">
        <b-skeleton width="20%" animated></b-skeleton>
        <b-skeleton width="40%" animated></b-skeleton>
        <b-skeleton width="80%" animated></b-skeleton>
        <b-skeleton animated></b-skeleton>
      </div>
      <div v-if="profile !== null && contests !== null">
        <b-message type="is-warning" has-icon v-if="!profileComplete">
          Dein Profil ist noch nicht fertig ausgefüllt. Damit du dich für
          Trainingscamps und den Bundesbewerb qualifizieren kannst, musst du
          diese in den
          <router-link :to="{ name: 'Profile' }"
            >Profileinstellungen</router-link
          >
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
        <h1 class="title">Wettbewerbe</h1>
        <div class="block">
          <p>Hier kannst du dich bei unseren Wettbewerbsservern anmelden.</p>
        </div>

        <div class="contests-container">
          <ContestCard
            :contest="contest"
            :profileComplete="profileComplete"
            v-for="contest in activeContests"
            :key="contest.uuid"
          />
        </div>

        <template v-if="archivedContests.length">
          <hr class="mt-6 mb-6" />
          <h1 class="title">Archivierte Wettbewerbe</h1>
          <div class="block">
            <p>Hier findest du ältere Wettbewerbe.</p>
          </div>
          <div class="contests-container">
            <ContestCard
              :contest="contest"
              :profileComplete="profileComplete"
              v-for="contest in archivedContests"
              :key="contest.uuid"
            />
          </div>
        </template>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Contests } from "@/types/contests";
import contests from "@/services/contests";
import ContestCard from "./ContestCard.vue";
import { ProfileInfoResponse } from "@/types/profile";
import profile from "@/services/profile";

@Component({
  components: {
    ContestCard,
  },
})
export default class HomeContests extends Vue {
  contests: Contests | null = null;
  profile: ProfileInfoResponse | null = null;
  showLoading = false;

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

  get activeContests(): Contests | null {
    if (this.contests === null) return null;
    return this.contests.filter((c) => !c.archived);
  }

  get archivedContests(): Contests | null {
    if (this.contests === null) return null;
    return this.contests.filter((c) => c.archived);
  }

  async loadProfile() {
    this.profile = await profile.profileInfo();
  }
  async loadContests() {
    this.contests = await contests.listContests();
  }

  async mounted() {
    setTimeout(() => (this.showLoading = true), 500);
    await Promise.all([this.loadContests(), this.loadProfile()]);
  }
}
</script>

<style scoped>
.contests-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
@media screen and (max-width: 768px) {
  .contests-container {
    grid-template-columns: repeat(1, 1fr);
  }
}
</style>
