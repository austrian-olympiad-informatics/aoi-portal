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
          Trainingscamps und den Bundesbewerb qualifizieren kannst, musst du diese
          in den
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
              <b-checkbox class="mb-3" required>
                Ich verstehe, dass diese Qualifikation eine Einzelarbeit ist.
                Gruppenarbeiten sowie das Teilen von Lösungen sind nicht erlaubt.
              </b-checkbox>
            </div>
            <b-button 
              expanded 
              native-type="submit"
              type="is-primary"
            >
              Teilnehmen / Bei diesem Bewerb registrieren
            </b-button>
            <p class="mt-4" v-if="contest.quali_round">
              <em>Hinweis:</em> Wir veröffentlichen nach dem Wettbewerb eine
              Ergebnisliste der besten Teilnehmer:innen auf unserer Webseite.
              Wenn dein Name auf dieser Liste anonymisiert (Vor- und Nachname mit N., N. ersetzt) aufscheinen soll, kannst du uns eine E-Mail mit deinem
              Wunsch an <a href="mailto:orga@informatikolympiade.at">orga@informatikolympiade.at</a>
              schicken.
            </p>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import contests from "@/services/contests";
import { ContestDetail } from "@/types/contests";
import profile from "@/services/profile";
import { ProfileInfoResponse } from "@/types/profile";

@Component
export default class ContestView extends Vue {
  contestUuid!: string;
  contest: ContestDetail | null = null;
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

  async loadContest() {
    this.contest = await contests.getContest(this.contestUuid);
  }
  async loadProfile() {
    this.profile = await profile.profileInfo();
  }

  async mounted() {
    setTimeout(() => (this.showLoading = true), 500);
    this.contestUuid = this.$route.params.contestUuid;
    await Promise.all([this.loadContest(), this.loadProfile()]);
  }

  async doJoinContest() {
    await contests.joinContest(this.contestUuid);
    this.$buefy.toast.open({
      message:
        "Erfolgreich bei Wettbewerb registriert!",
      type: "is-success",
    });
    await this.loadContest();
  }

  async joinContest() {
    if (this.contest?.quali_round && !this.profileComplete) {
      this.$buefy.dialog.confirm({
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
          this.doJoinContest();
        },
      });
    } else {
      await this.doJoinContest();
    }
  }
}
</script>
