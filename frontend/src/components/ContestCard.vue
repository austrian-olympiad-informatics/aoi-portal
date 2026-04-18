<template>
  <div class="card">
    <div class="card-content">
      <div class="mb-3">
        <p class="title is-4 mb-3">
          {{ contest.name }}
        </p>
        <div
          v-if="contest.joined && contest.quali_round && !profileComplete"
          class="profile-warning"
        >
          <span class="icon-text">
            <b-icon icon="alert"></b-icon>
            <router-link :to="{ name: 'Profile' }"
              >Ausgefülltes Profil</router-link
            >&nbsp; für Qualifizieren notwendig.
          </span>
        </div>
        <div
          v-if="contest.joined && contest.quali_round && profileComplete"
          class="profile-success"
        >
          <span class="icon-text">
            <b-icon icon="check-circle"></b-icon>
            Alle Daten für qualifizieren vorhanden.
          </span>
        </div>
        <div class="content" v-html="contest.teaser"></div>
      </div>

      <div class="buttons">
        <b-button
          tag="router-link"
          icon-right="chevron-right"
          class="is-pulled-right"
          :to="{
            name: 'Contest',
            params: { contestUuid: contest.uuid },
          }"
          >Details</b-button
        >
        <template v-if="contest.joined">
          <b-button
            v-if="contest.allow_frontendv2"
            tag="router-link"
            icon-right="chevron-right"
            class="is-pulled-right"
            :to="{
              name: 'CMSContest',
              params: { contestName: contest.cms_name },
            }"
            type="is-success is-light"
            >Zum Bewerb</b-button
          >
          <b-button
            v-else-if="contest.sso_enabled"
            tag="router-link"
            icon-right="chevron-right"
            class="is-pulled-right"
            :to="{
              name: 'ContestSSO',
              params: { contestUuid: contest.uuid },
            }"
            type="is-success is-light"
            >Zum Server</b-button
          >
          <b-button
            v-else
            tag="a"
            icon-right="chevron-right"
            class="is-pulled-right"
            :href="contest.url"
            type="is-success is-light"
            >Zum Server</b-button
          >
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import contests from "@/services/contests";
import { Contest } from "@/types/contests";

// NOTE: profileComplete is typed as Contest in the original — this appears to be
// a bug (should be boolean). Preserved as-is; tracked for separate fix.
const props = defineProps<{
  contest: Contest;
  profileComplete: Contest;
}>();

const emit = defineEmits<{ joined: [] }>();

async function joinContest() {
  await contests.joinContest(props.contest.uuid);
  emit("joined");
}
</script>

<style lang="scss" scoped>
.profile-warning {
  color: #946c00;
  padding: 0.75em 1.5em;
  background-color: #fffaeb;
  border-top: 2px dashed #ffe08a;
  border-bottom: 2px dashed #ffe08a;
  margin-left: -1.5rem;
  margin-right: -1.5rem;
  margin-bottom: 1rem;

  a {
    color: currentColor;
    text-decoration: underline;
  }
}
.profile-success {
  color: #257953;
  padding: 0.75em 1.5em;
  background-color: #effaf5;
  border-top: 2px dashed #48c78e;
  border-bottom: 2px dashed #48c78e;
  margin-left: -1.5rem;
  margin-right: -1.5rem;
  margin-bottom: 1rem;
}
.card-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.buttons {
  justify-content: flex-end;
}
</style>
