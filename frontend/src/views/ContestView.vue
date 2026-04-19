<template>
  <div class="container">
    <div class="section">
      <div v-if="(profile === null || contest === null) && showLoading">
        <b-skeleton width="20%" animated></b-skeleton>
        <b-skeleton width="40%" animated></b-skeleton>
        <b-skeleton width="80%" animated></b-skeleton>
        <b-skeleton animated></b-skeleton>
      </div>
      <div v-if="profile !== null && contest !== null">
        <b-message
          type="is-warning"
          has-icon
          v-if="contest.quali_round && !profileComplete"
        >
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
        <b-message
          type="is-success"
          has-icon
          v-if="contest.quali_round && profileComplete"
        >
          Alle Daten für qualifizieren vorhanden.
        </b-message>

        <h1 class="title is-3">{{ contest.name }}</h1>
        <div class="content" v-html="contest.description"></div>
        <hr />
        <template v-if="contest.joined">
          <b-button
            v-if="contest.allow_frontendv2"
            tag="router-link"
            icon-right="chevron-right"
            expanded
            type="is-primary"
            :to="{
              name: 'CMSContest',
              params: { contestName: contest.cms_name },
            }"
            >Zum Bewerb</b-button
          >
          <b-button
            v-else-if="contest.sso_enabled"
            tag="router-link"
            icon-right="chevron-right"
            expanded
            type="is-primary"
            :to="{
              name: 'ContestSSO',
              params: { contestUuid: contestUuid },
            }"
            >Zum Server</b-button
          >
          <b-button
            v-else
            tag="a"
            icon-right="chevron-right"
            expanded
            type="is-primary"
            :href="contest.url"
            >Zum Server</b-button
          >
        </template>
        <template v-else>
          <form @submit.prevent="joinContest">
            <div v-if="contest.quali_round">
              <b-checkbox required>
                Ich habe die
                <a href="https://informatikolympiade.at/regeln.html">
                  Teilnahmebedingungen
                </a>
                gelesen und akzeptiere diese.
              </b-checkbox>
              <b-checkbox required>
                Ich verstehe, dass diese Qualifikation eine Einzelarbeit ist.
                Gruppenarbeiten sowie das Teilen von Lösungen sind nicht
                erlaubt.
              </b-checkbox>
              <b-checkbox class="mb-3" required>
                Ich verstehe, dass die Verwendung von KI-Tools zur
                Codegenerierung und Lösungsfindung (wie GitHub Copilot, ChatGPT,
                etc.) verboten ist.
              </b-checkbox>
            </div>
            <b-button expanded native-type="submit" type="is-primary">
              Teilnehmen / Bei diesem Bewerb registrieren
            </b-button>
            <p class="mt-4" v-if="contest.quali_round">
              <em>Hinweis:</em> Wir veröffentlichen nach dem Wettbewerb eine
              Ergebnisliste der besten Teilnehmer:innen auf unserer Webseite.
              Wenn dein Name auf dieser Liste anonymisiert (Vor- und Nachname
              mit N., N. ersetzt) aufscheinen soll, kannst du uns eine E-Mail
              mit deinem Wunsch an
              <a href="mailto:orga@informatikolympiade.at"
                >orga@informatikolympiade.at</a
              >
              schicken.
            </p>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import { useStore } from "@/store";
import { useToast, useDialog } from "buefy";
import contests from "@/services/contests";
import { ContestDetail } from "@/types/contests";
import profileService from "@/services/profile";
import { ProfileInfoResponse } from "@/types/profile";

const route = useRoute();
const store = useStore();
const toast = useToast();
const dialog = useDialog();

const contestUuid = ref("");
const contest = ref<ContestDetail | null>(null);
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

async function loadContest() {
  contest.value = await contests.getContest(contestUuid.value);
}

async function loadProfile() {
  if (store.isProxyAuth) {
    profile.value = {} as ProfileInfoResponse;
    return;
  }
  profile.value = await profileService.profileInfo();
}

onMounted(async () => {
  setTimeout(() => (showLoading.value = true), 500);
  contestUuid.value = route.params.contestUuid as string;
  await Promise.all([loadContest(), loadProfile()]);
});

async function doJoinContest() {
  await contests.joinContest(contestUuid.value);
  toast.open({
    message: "Erfolgreich bei Wettbewerb registriert!",
    type: "is-success",
  });
  await loadContest();
}

async function joinContest() {
  if (contest.value?.quali_round && !profileComplete.value) {
    dialog.confirm({
      title: "Ausgefülltes Profil notwendig",
      message: `
        <div class="content">
          <p>
            <strong>Dein Profil ist noch nicht vollständig ausgefüllt. </strong>
          </p>
          <p>
            <strong>Nur vollständig ausgefüllte Profile können für die Qualifikation berücksichtigt werden.</strong>
          </p>
          <p>
            <i>Hinweis</i>: Du kannst dich auch ohne Profildaten anmelden, und so bspw. die Angaben
            anschauen und das Abgabesystem testen. Achte aber darauf, dass du bis zum Ende der
            Qualifikation diese Informationen ausgefüllt haben musst.
          </p>
        </div>
          `,
      confirmText: "Trotzdem Weiter",
      type: "is-warning",
      onConfirm: () => {
        doJoinContest();
      },
    });
  } else {
    await doJoinContest();
  }
}
</script>
