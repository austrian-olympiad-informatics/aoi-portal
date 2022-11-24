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
        <router-link
          :to="{ name: 'CMSAdminSubmissions', query: { user_id: userId } }"
        >
          {{ submissions.total }} submissions
        </router-link>
      </div>
      <div class="block" v-if="userEvals !== null">
        <h2 class="title is-4">User Evals</h2>
        <router-link
          :to="{ name: 'CMSAdminUserEvals', query: { user_id: userId } }"
        >
          {{ userEvals.total }} user evals
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
      <div class="block" v-if="registerInfo !== null">
        <h2 class="title is-4">Register Info</h2>
        <b>Vorname:</b> {{ registerInfo.first_name }} <br />
        <b>Nachname:</b> {{ registerInfo.last_name }} <br />
        <b>Email:</b>
        <a :href="`mailto:${registerInfo.email}`"> {{ registerInfo.email }} </a>
        <br />
        <b>Adresse:</b>
        {{ registerInfo.address_street ? registerInfo.address_street : "N/A" }}
        <br />
        <b>Stadt:</b>
        {{ registerInfo.address_town ? registerInfo.address_town : "N/A" }}
        <br />
        <b>PLZ:</b>
        {{ registerInfo.address_zip ? registerInfo.address_zip : "N/A" }}
        <br />
        <b>Geburtstag:</b>
        {{ registerInfo.birthday ? registerInfo.birthday : "N/A" }} <br />
        <b>CMS Username:</b>
        {{
          registerInfo.cms_username
            ? `${registerInfo.cms_username} (#${registerInfo.cms_id})`
            : "N/A"
        }}
        <br />
        <b>Erstellt am:</b> {{ registerInfo.created_at }} <br />
        <b>Admin?</b> {{ registerInfo.is_admin }} <br />
        <b>Telefonnummer:</b>
        {{ registerInfo.phone_nr ? registerInfo.phone_nr : "N/A" }} <br />
        <b>Schule:</b>
        {{ registerInfo.school_name ? registerInfo.school_name : "N/A" }} <br />
        <b>Schuladresse:</b>
        {{ registerInfo.school_address ? registerInfo.school_address : "N/A" }}
        <br />
        <div class="buttons is-pulled-right">
          <b-button
            tag="router-link"
            :to="{ name: 'AdminUser', params: { userId: registerInfo.id } }"
            icon-left="pencil"
            type="is-warning"
          >
            Edit
          </b-button>
        </div>
      </div>
      <div class="block">
        <h2 class="title is-4">Participations</h2>
        <ul>
          <li v-for="part in user.participations" :key="part.id">
            <router-link
              :to="{
                name: 'CMSAdminContest',
                params: { contestId: part.contest.id },
              }"
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
import admin from "@/services/admin";
import {
  AdminUser,
  AdminSubmissionsPaginated,
  AdminUserEvalsPaginated,
} from "@/types/cmsadmin";
import { AdminUser as AdminRegisterUser } from "@/types/admin";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class AdminUserView extends Vue {
  get userId(): number {
    return +this.$route.params.userId;
  }
  user: AdminUser | null = null;
  submissions: AdminSubmissionsPaginated | null = null;
  userEvals: AdminUserEvalsPaginated | null = null;
  registerInfo: AdminRegisterUser | null = null;

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
  async loadUserEvals() {
    this.userEvals = await cmsadmin.getUserEvals({
      userId: this.userId,
      perPage: 0,
    });
  }
  async loadRegisterData() {
    const users = await admin.getUsers();
    for (const user of users) {
      if (user.cms_id === this.userId) {
        this.registerInfo = user;
        return;
      }
    }
  }
  async mounted() {
    await Promise.all([
      this.loadUser(),
      this.loadSubmissions(),
      this.loadUserEvals(),
      this.loadRegisterData(),
    ]);
  }
}
</script>
