<template>
  <div class="container">
    <section class="section">
      <h1 class="title is-2">CMS Admin Panel</h1>
      <div class="block">
        <h2 class="title is-4">Contests</h2>
        <template v-if="contests !== null">
          <ul>
            <li v-for="contest in contests" :key="contest.id">
              <router-link
                :to="{
                  name: 'CMSAdminContest',
                  params: {
                    contestId: contest.id,
                  },
                }"
              >
                {{ contest.description }} ({{ contest.name }})
              </router-link>
            </li>
          </ul>
        </template>
        <template v-else>
          <b-loading :is-full-page="false" :active="true" />
        </template>
      </div>
      <div class="block">
        <h2 class="title is-4">Tasks</h2>
        <template v-if="tasks !== null">
          <ul>
            <li v-for="task in tasks" :key="task.id">
              <router-link
                :to="{
                  name: 'CMSAdminTask',
                  params: {
                    taskId: task.id,
                  },
                }"
              >
                {{ task.name }} - {{ task.title }} ({{
                  task.contest ? task.contest.description : "No Contest"
                }})
              </router-link>
            </li>
          </ul>
        </template>
        <template v-else>
          <b-loading :is-full-page="false" :active="true" />
        </template>
      </div>
      <div class="block">
        <h2 class="title is-4">Users</h2>
        <template v-if="users !== null">
          <ul>
            <li v-for="user in users" :key="user.id">
              <router-link
                :to="{
                  name: 'CMSAdminUser',
                  params: {
                    userId: user.id,
                  },
                }"
              >
                {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
              </router-link>
            </li>
          </ul>
        </template>
        <template v-else>
          <b-loading :is-full-page="false" :active="true" />
        </template>
      </div>
      <div class="block">
        <h2 class="title is-4">Memes</h2>
        <template v-if="memes !== null">
          <ul>
            <li v-for="meme in memes" :key="meme.id">Meme {{ meme }}</li>
          </ul>
        </template>
        <template v-else>
          <b-loading :is-full-page="false" :active="true" />
        </template>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import cmsadmin from "@/services/cmsadmin";
import {
  AdminContests,
  AdminUsers,
  AdminAllTasks,
  AdminMemes,
} from "@/types/cmsadmin";

const contests = ref<AdminContests | null>(null);
const tasks = ref<AdminAllTasks | null>(null);
const users = ref<AdminUsers | null>(null);
const memes = ref<AdminMemes | null>(null);

onMounted(async () => {
  await Promise.all([
    cmsadmin.getContests().then((v) => { contests.value = v; }),
    cmsadmin.getTasks().then((v) => { tasks.value = v; }),
    cmsadmin.getUsers().then((v) => { users.value = v; }),
    cmsadmin.getMemes().then((v) => { memes.value = v; }),
  ]);
});
</script>
