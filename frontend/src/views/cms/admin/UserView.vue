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
        <b>Teilnahmeberechtigung:</b>
        {{ eligibilityLabel(registerInfo.eligibility) }}
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
          <div v-for="part in user.participations" :key="part.id">
            <UserContest
              :part-id="part.id"
              :user-id="userId"
              :contest="part.contest"
            />
          </div>
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
import admin from "@/services/admin";
import {
  AdminUser,
  AdminSubmissionsPaginated,
  AdminUserEvalsPaginated,
} from "@/types/cmsadmin";
import { AdminUser as AdminRegisterUser } from "@/types/admin";
import UserContest from "./UserContestComponent.vue";

const route = useRoute();

const userId = computed(() => +route.params.userId);
const user = ref<AdminUser | null>(null);
const submissions = ref<AdminSubmissionsPaginated | null>(null);
const userEvals = ref<AdminUserEvalsPaginated | null>(null);
const registerInfo = ref<AdminRegisterUser | null>(null);

const fullName = computed(() => {
  if (user.value === null) return null;
  return `${user.value.first_name} ${user.value.last_name} (${user.value.username})`;
});

async function loadUser() {
  user.value = await cmsadmin.getUser(userId.value);
}
async function loadSubmissions() {
  submissions.value = await cmsadmin.getSubmissions({
    userId: userId.value,
    perPage: 0,
  });
}
async function loadUserEvals() {
  userEvals.value = await cmsadmin.getUserEvals({
    userId: userId.value,
    perPage: 0,
  });
}
async function loadRegisterData() {
  const users = await admin.getUsers();
  for (const u of users) {
    if (u.cms_id === userId.value) {
      registerInfo.value = u;
      return;
    }
  }
}

onMounted(async () => {
  await Promise.all([
    loadUser(),
    loadSubmissions(),
    loadUserEvals(),
    loadRegisterData(),
  ]);
});

function eligibilityLabel(eligibility: string | null): string {
  if (eligibility === "ioi") return "IOI";
  if (eligibility === "ioi_egoi") return "IOI + EGOI";
  return "-";
}
</script>
