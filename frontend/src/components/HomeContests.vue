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

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useStore } from "@/store";
import { Contests } from "@/types/contests";
import contestsService from "@/services/contests";
import ContestCard from "./ContestCard.vue";
import { ProfileInfoResponse } from "@/types/profile";
import profileService from "@/services/profile";

const store = useStore();

const contests = ref<Contests | null>(null);
const profile = ref<ProfileInfoResponse | null>(null);
const showLoading = ref(false);

const profileComplete = computed((): boolean => {
  if (profile.value === null) return true;
  return !!(
    profile.value.first_name &&
    profile.value.last_name &&
    profile.value.birthday &&
    profile.value.phone_nr &&
    profile.value.address_street &&
    profile.value.address_zip &&
    profile.value.address_town &&
    profile.value.school_name &&
    profile.value.school_address
  );
});

const activeContests = computed((): Contests | null => {
  if (contests.value === null) return null;
  return contests.value.filter((c) => !c.archived);
});

const archivedContests = computed((): Contests | null => {
  if (contests.value === null) return null;
  return contests.value.filter((c) => c.archived);
});

async function loadProfile() {
  if (store.isProxyAuth) {
    profile.value = {} as ProfileInfoResponse;
    return;
  }
  profile.value = await profileService.profileInfo();
}

async function loadContests() {
  contests.value = await contestsService.listContests();
}

onMounted(async () => {
  setTimeout(() => (showLoading.value = true), 500);
  await Promise.all([loadContests(), loadProfile()]);
});
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
