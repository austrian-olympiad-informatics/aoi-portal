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
          active
        >
          {{ contest.description }}
        </b-breadcrumb-item>
      </b-breadcrumb>
      <h1 class="title is-2">Admin - Contest {{ contest.description }}</h1>
      <div class="block">
        <ul>
          <li>ID: {{ contest.id }}</li>
          <li>Name: {{ contest.name }}</li>
          <li>Description: {{ contest.description }}</li>
          <li>
            Start/End: {{ formatDate(contest.start) }} /
            {{ formatDate(contest.stop) }}
          </li>
          <li v-if="contest.analysis !== null">
            Analysis: {{ formatDate(contest.stop) }}
          </li>
          <li v-else>Analysis: Disabled</li>
          <li>Score precision: {{ contest.score_precision }}</li>
          <li>
            Languages:
            <span v-for="(lang, i) in contest.languages" :key="lang">
              <code>{{ lang }}</code>
              <span v-if="i + 1 < contest.languages.length">, </span>
            </span>
          </li>
          <li>Allow frontend v2: {{ contest.allow_frontendv2 }}</li>
        </ul>
      </div>
      <div class="block">
        <h2 class="title is-4">Tasks</h2>
        <ul>
          <li v-for="task in contest.tasks" :key="task.id">
            <router-link
              :to="{ name: 'CMSAdminTask', params: { taskId: task.id } }"
            >
              {{ task.name }} {{ task.title }}
            </router-link>
          </li>
        </ul>
      </div>
      <div class="block" v-if="participations !== null">
        <h2 class="title is-4">Participants</h2>
        <ul>
          <li v-for="part in participations" :key="part.id">
            <router-link
              :to="{ name: 'CMSAdminUser', params: { userId: part.user.id } }"
            >
              {{ part.user.first_name }} {{ part.user.last_name }} ({{
                part.user.username
              }})
            </router-link>
          </li>
        </ul>
      </div>
      <div class="block" v-if="submissions !== null">
        <h2 class="title is-4">Submissions</h2>
        <router-link
          :to="{
            name: 'CMSAdminSubmissions',
            query: { contest_id: contestId },
          }"
        >
          {{ submissions.total }} submissions
        </router-link>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import cmsadmin from "@/services/cmsadmin";
import {
  AdminContest,
  AdminContestParticipations,
  AdminSubmissionsPaginated,
} from "@/types/cmsadmin";
import { formatDateShort } from "@/util/dt";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class AdminContestView extends Vue {
  get contestId(): number {
    return +this.$route.params.contestId;
  }
  contest: AdminContest | null = null;
  participations: AdminContestParticipations | null = null;
  submissions: AdminSubmissionsPaginated | null = null;

  async loadContest() {
    this.contest = await cmsadmin.getContest(this.contestId);
  }
  async loadParticipations() {
    this.participations = await cmsadmin.getContestParticipations(
      this.contestId
    );
  }
  async loadSubmissions() {
    this.submissions = await cmsadmin.getSubmissions({
      contestId: this.contestId,
      perPage: 0,
    });
  }
  async mounted() {
    await Promise.all([
      this.loadContest(),
      this.loadParticipations(),
      this.loadSubmissions(),
    ]);
  }
  formatDate(date: string) {
    return formatDateShort(new Date(), new Date(date));
  }
}
</script>
