<template>
  <div class="container">
    <section class="section" v-if="user !== null">
      <b-breadcrumb align="is-left" size="is-left">
        <b-breadcrumb-item tag="router-link" :to="{ name: 'CMSAdminIndex' }">
          Admin Panel
        </b-breadcrumb-item>
        <b-breadcrumb-item
          tag="router-link"
          :to="{ name: 'CMSAdminUser', params: { userId } }"
          active
        >
          {{ fullName }}
        </b-breadcrumb-item>
      </b-breadcrumb>
      <h1 class="title is-2">Admin - User {{ fullName }}</h1>
      <div class="block" v-if="submissions !== null">
        <h2 class="title is-4">Submissions</h2>
        <router-link :to="{ name: 'CMSAdminSubmissions', query: { task_id: taskId } }">
          {{ submissions.total }} submissions
        </router-link>
      </div>
      <div class="block">
        <h2 class="title is-4">Info</h2>
        <ul>
          <li>ID: {{ user.id }}</li>
          <li>First name: {{ user.first_name }}</li>
          <li>Last name: {{ user.last_name }}</li>
          <li>Username: {{ user.username }}</li>
        </ul>
      </div>
      <div class="block">
        <h2 class="title is-4">Participations</h2>
        <ul>
          <li v-for="part in user.participations" :key="part.id">
            <router-link
              :to="{ name: 'CMSAdminContest', params: { contestId: part.contest.id }}"
            >
              {{ part.contest.name }}
            </router-link>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import cmsadmin from "@/services/cmsadmin";
import { AdminUser, AdminContestParticipations, AdminSubmissionsPaginated } from "@/types/cmsadmin";
import { formatDateShort } from "@/util/dt";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class AdminUserView extends Vue {
  get userId(): number {
    return +this.$route.params.userId;
  }
  user: AdminUser | null = null;
  submissions: AdminSubmissionsPaginated | null = null;

  get fullName() {
    if (this.user === null) return null;
    return `${this.user.first_name} ${this.user.last_name} (${this.user.username})`;
  }

  async loadUser() {
    this.user = await cmsadmin.getUser(this.userId);
  }
  async loadSubmissions() {
    this.submissions = await cmsadmin.getSubmissions({
      userId: this.userId,
      perPage: 0,
    });
  }
  async mounted() {
    await Promise.all([this.loadUser(), this.loadSubmissions()]);
  }
}
</script>
