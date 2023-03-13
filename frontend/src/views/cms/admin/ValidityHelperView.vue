<template>
  <div class="container">
    <section class="section" v-if="contest !== null">
      <b-breadcrumb align="is-left" size="is-left">
        <b-breadcrumb-item tag="router-link" :to="{ name: 'CMSAdminIndex' }">
          Admin Panel
        </b-breadcrumb-item>
        <b-breadcrumb-item
          tag="router-link"
          :to="{ name: 'CMSAdminContest', params: { contestId } }"
        >
          {{ contest.description }}
        </b-breadcrumb-item>
        <b-breadcrumb-item
          tag="router-link"
          :to="{ name: 'CMSAdminValidityHelper', params: { contestId } }"
          active
        >
          Ranking
        </b-breadcrumb-item>
      </b-breadcrumb>
      <h1 class="title is-2">Admin - Ranking {{ contest.description }}</h1>

      <b-button @click="downloadCSV" type="is-primary">
        Download as CSV
      </b-button>

      <b-table
        :data="tableData"
        hoverable
        v-if="tableData !== null"
        :mobile-cards="false"
        detailed
        detail-key="id"
      >
        <b-table-column label="#" v-slot="props">
          <span v-if="!props.row.hidden">{{ props.row.rank }}</span>
        </b-table-column>
        <b-table-column label="Name" v-slot="props">
          {{ props.row.first_name }} {{ props.row.last_name }}
        </b-table-column>
        <b-table-column label="Score" v-slot="props" width="25%">
          <PointsBar
            v-if="props.row.score !== undefined"
            :score="props.row.score"
            :max-score="maxScore"
            :score-precision="scorePrecision"
            :show-max-score="false"
            :subtasks="null"
          />
        </b-table-column>
        <b-table-column label="Birthday" v-slot="props">
          {{ props.row.birthday }}
        </b-table-column>
        <b-table-column label="School" v-slot="props">
          {{ props.row.school_name }}
        </b-table-column>
        <b-table-column label="Hidden" v-slot="props" centered>
          <b-icon icon="eye-off" v-if="props.row.hidden" />
        </b-table-column>
        <b-table-column label="Warning" v-slot="props">
          <b-tooltip
            label="User should be hidden"
            v-if="warnShouldBeHidden(props.row)"
          >
            <b-icon icon="alert-octagon" class="has-text-danger" />
          </b-tooltip>
          <b-tooltip
            label="User should not be hidden"
            v-else-if="warnShouldNotBeHidden(props.row)"
          >
            <b-icon icon="alert-octagon" class="has-text-info" />
          </b-tooltip>
          <b-tooltip
            label="User has bad birthday"
            v-else-if="warnBadBirthday(props.row)"
          >
            <b-icon icon="alert" class="has-text-warning" />
          </b-tooltip>
          <b-tooltip
            label="No corresponding portal account"
            v-else-if="props.row.portal_id === undefined"
          >
            <b-icon icon="alert" />
          </b-tooltip>
        </b-table-column>

        <template #detail="props">
          <b>Vorname:</b> {{ props.row.first_name }} <br />
          <b>Nachname:</b> {{ props.row.last_name }} <br />
          <b>Email:</b>
          <a :href="`mailto:${props.row.email}`"> {{ props.row.email }} </a>
          <br />
          <b-field>
            <b-switch
              :value="props.row.hidden"
              @input="(v) => changeHidden(props.row.id, v)"
              >Hidden</b-switch
            >
          </b-field>
          <div v-if="props.row.portal_id !== undefined">
            <b>Adresse:</b>
            {{ props.row.address_street ? props.row.address_street : "N/A" }}
            <br />
            <b>Stadt:</b>
            {{ props.row.address_town ? props.row.address_town : "N/A" }} <br />
            <b>PLZ:</b>
            {{ props.row.address_zip ? props.row.address_zip : "N/A" }}
            <br />
            <b>Geburtstag:</b>
            {{ props.row.birthday ? props.row.birthday : "N/A" }} <br />
            <b>Username:</b>
            {{ props.row.username }}
            <br />
            <b>Erstellt am:</b> {{ props.row.created_at }} <br />
            <b>Admin?</b> {{ props.row.is_admin }} <br />
            <b>Telefonnummer:</b>
            {{ props.row.phone_nr ? props.row.phone_nr : "N/A" }} <br />
            <b>Schule:</b>
            {{ props.row.school_name ? props.row.school_name : "N/A" }} <br />
            <b>Schuladresse:</b>
            {{ props.row.school_address ? props.row.school_address : "N/A" }}
            <br />
            <router-link
              :to="{
                name: 'AdminUser',
                params: { userId: props.row.portal_id },
              }"
            >
              Edit register details
            </router-link>
            <br />
          </div>
          <div v-else>
            <b-message type="is-warning">
              This user has no corresponding portal account.
            </b-message>
          </div>

          <router-link
            :to="{
              name: 'CMSAdminSubmissions',
              query: { user_id: props.row.user_id, contest_id: contestId },
            }"
          >
            User submissions
          </router-link>
          <br />
          <UserContest
            class="mt-3"
            v-if="contest !== null"
            :part-id="props.row.id"
            :user-id="props.row.user_id"
            :contest="contest"
          />
        </template>
      </b-table>
    </section>
  </div>
</template>

<script lang="ts">
import cmsadmin from "@/services/cmsadmin";
import admin from "@/services/admin";
import {
  AdminContest,
  AdminContestParticipations,
  AdminContestRanking,
} from "@/types/cmsadmin";
import { AdminUser as AdminRegisterUser } from "@/types/admin";
import { Component, Vue } from "vue-property-decorator";
import PointsBar from "../PointsBar.vue";
import UserContest from "./UserContestComponent.vue";

@Component({
  components: {
    PointsBar,
    UserContest,
  },
})
export default class AdminValidityHelperView extends Vue {
  get contestId(): number {
    return +this.$route.params.contestId;
  }
  contest: AdminContest | null = null;
  registerDatas: Map<number, AdminRegisterUser> | null = null;
  participations: AdminContestParticipations | null = null;
  scores: AdminContestRanking | null = null;

  async loadContest() {
    this.contest = await cmsadmin.getContest(this.contestId);
  }
  async loadParticipations() {
    this.participations = await cmsadmin.getContestParticipations(
      this.contestId
    );
  }
  async loadRegisterData() {
    const users = await admin.getUsers();
    this.registerDatas = new Map(
      users.filter((u) => u.cms_id !== null).map((u) => [u.cms_id as number, u])
    );
  }
  async loadScores() {
    this.scores = await cmsadmin.getContestRanking(this.contestId);
  }

  get scoresByPart() {
    if (this.scores === null) {
      return null;
    }
    return new Map(this.scores.results.map((p) => [p.id, p]));
  }

  get tableData() {
    const scoresPart = this.scoresByPart;
    if (
      this.participations === null ||
      this.registerDatas === null ||
      this.scores === null ||
      scoresPart === null
    ) {
      return [];
    }
    const res = this.participations.map((p) => {
      const score = scoresPart.get(p.id);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let x: any = {
        id: p.id,
        hidden: p.hidden,
        user_id: p.user.id,
        first_name: p.user.first_name,
        last_name: p.user.last_name,
        username: p.user.username,
      };
      const user = this.registerDatas!.get(p.user.id);
      if (user !== undefined) {
        x = {
          ...x,
          first_name: user.first_name,
          last_name: user.last_name,
          email: user.email,
          created_at: user.created_at,
          last_login: user.last_login,
          is_admin: user.is_admin,
          birthday: user.birthday,
          phone_nr: user.phone_nr,
          address_street: user.address_street,
          address_zip: user.address_zip,
          address_town: user.address_town,
          school_name: user.school_name,
          school_address: user.school_address,
          portal_id: user.id,
        };
      }
      if (score !== undefined) {
        x = {
          ...x,
          score: score.score,
          rank: score.rank,
          task_scores: score.task_scores,
        };
      }
      return x;
    });
    res.sort((a, b) => {
      if (a.score === undefined) {
        return 1;
      }
      if (b.score === undefined) {
        return -1;
      }
      return b.score - a.score;
    });
    return res;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  warnShouldBeHidden(row: any) {
    if (row.portal_id === undefined) return !row.hidden;
    if (row.hidden) return false;
    if (!row.school_name) return true;
    if (!row.birthday) return true;
    const birthday = new Date(row.birthday);
    if (birthday.getFullYear() < 2003) return true;
    return false;
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  warnShouldNotBeHidden(row: any) {
    if (row.portal_id === undefined) return false;
    if (!row.hidden) return false;
    if (!row.school_name) return false;
    if (!row.birthday) return false;
    const birthday = new Date(row.birthday);
    return birthday.getFullYear() >= 2003 && birthday.getFullYear() <= 2016;
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  warnBadBirthday(row: any) {
    if (row.portal_id === undefined) return false;
    if (!row.birthday) return false;
    const birthday = new Date(row.birthday);
    return birthday.getFullYear() > 2016;
  }

  get maxScore() {
    if (this.scores === null) return 0;
    return this.scores.tasks.reduce((acc, task) => acc + task.max_score, 0);
  }
  get scorePrecision() {
    if (this.scores === null) return 0;
    return this.scores.score_precision;
  }

  async changeHidden(partId: number, hidden: boolean) {
    await cmsadmin.updateParticipation(partId, { hidden });
    await this.loadParticipations();
  }

  async mounted() {
    await Promise.all([
      this.loadContest(),
      this.loadParticipations(),
      this.loadRegisterData(),
      this.loadScores(),
    ]);
  }

  downloadCSV() {
    // https://stackoverflow.com/a/20623188
    const encodeRow = (row: string[]): string => {
      return row
        .map((s) => {
          s = s.replace(/"/g, '""');
          if (s.search(/("|,|\n)/g) >= 0) s = `"${s}"`;
          return s;
        })
        .join(",");
    };
    const header = [
      "Rank",
      "First Name",
      "Last Name",
      "Email",
      "Created At",
      "Birthday",
      "Phone Nr",
      "Address Street",
      "Address Zip",
      "Address Town",
      "School Name",
      "School Address",
      "Username",
      "Score",
      ...this.scores!.tasks.map((x) => x.name),
    ];
    const rows = [header];
    for (const row of this.tableData) {
      if (row.hidden || row.created_at === undefined) continue;
      rows.push([
        row.rank.toString(),
        row.first_name,
        row.last_name,
        row.email,
        row.created_at,
        row.birthday || "N/A",
        row.phone_nr || "N/A",
        row.address_street || "N/A",
        row.address_zip || "N/A",
        row.address_town || "N/A",
        row.school_name || "N/A",
        row.school_address || "N/A",
        row.username,
        row.score.toString(),
        ...this.scores!.tasks.map((x) => {
          return (
            row
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              .task_scores!.find((y: any) => x.id == y.id)
              .score.toString()
          );
        }),
      ]);
    }
    const csvContent = rows.map((r) => encodeRow(r)).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(blob);
    anchor.download = "ranking.csv";
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
  }
}
</script>
