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
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <h1 class="title is-2 mb-0">Admin - Contest {{ contest.description }}</h1>
          </div>
        </div>
        <div class="level-right" v-if="contest.portal_uuid !== null">
          <div class="level-item">
            <b-button
              tag="router-link"
              icon-left="pencil"
              :to="{
                name: 'AdminContest',
                params: { contestUuid: contest.portal_uuid },
              }"
            >
              Edit
            </b-button>
          </div>
        </div>
      </div>
      <div class="block" v-if="submissions !== null">
        <h2 class="title is-4">Submissions</h2>
        <router-link
          :to="{
            name: 'CMSAdminSubmissions',
            query: { contest_id: contestId },
          }"
        >
          {{ submissions.total }} submissions </router-link
        ><br />
        <router-link
          :to="{
            name: 'CMSAdminValidityHelper',
            params: { contestId: contestId },
          }"
        >
          Ranking
        </router-link>
      </div>
      <div class="block" v-if="userEvals !== null">
        <h2 class="title is-4">User Evals</h2>
        <router-link
          :to="{
            name: 'CMSAdminUserEvals',
            query: { contest_id: contestId },
          }"
        >
          {{ userEvals.total }} user evals
        </router-link>
      </div>
      <div class="block">
        <h2 class="title is-4">Settings</h2>
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
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import cmsadmin from "@/services/cmsadmin";
import {
  AdminContest,
  AdminContestParticipations,
  AdminSubmissionsPaginated,
  AdminUserEvalsPaginated,
} from "@/types/cmsadmin";
import { formatDateShort } from "@/util/dt";

const route = useRoute();

const contestId = computed(() => +route.params.contestId);
const contest = ref<AdminContest | null>(null);
const participations = ref<AdminContestParticipations | null>(null);
const submissions = ref<AdminSubmissionsPaginated | null>(null);
const userEvals = ref<AdminUserEvalsPaginated | null>(null);

async function loadContest() {
  contest.value = await cmsadmin.getContest(contestId.value);
}
async function loadParticipations() {
  participations.value = await cmsadmin.getContestParticipations(contestId.value);
}
async function loadSubmissions() {
  submissions.value = await cmsadmin.getSubmissions({
    contestId: contestId.value,
    perPage: 0,
  });
}
async function loadUserEvals() {
  userEvals.value = await cmsadmin.getUserEvals({
    contestId: contestId.value,
    perPage: 0,
  });
}

onMounted(async () => {
  await Promise.all([
    loadContest(),
    loadParticipations(),
    loadSubmissions(),
    loadUserEvals(),
  ]);
});

function formatDate(date: string) {
  return formatDateShort(new Date(), new Date(date));
}
</script>
