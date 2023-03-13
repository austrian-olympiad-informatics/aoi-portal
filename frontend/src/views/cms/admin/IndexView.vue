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

<script lang="ts">
import cmsadmin from "@/services/cmsadmin";
import {
  AdminContests,
  AdminUsers,
  AdminAllTasks,
  AdminMemes,
} from "@/types/cmsadmin";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class AdminIndexView extends Vue {
  contests: AdminContests | null = null;
  tasks: AdminAllTasks | null = null;
  users: AdminUsers | null = null;
  memes: AdminMemes | null = null;

  async loadContests() {
    this.contests = await cmsadmin.getContests();
  }
  async loadTasks() {
    this.tasks = await cmsadmin.getTasks();
  }
  async loadUsers() {
    this.users = await cmsadmin.getUsers();
  }
  async loadMemes() {
    this.memes = await cmsadmin.getMemes();
  }
  async mounted() {
    await Promise.all([
      this.loadContests(),
      this.loadTasks(),
      this.loadUsers(),
      this.loadMemes(),
    ]);
  }
}
</script>
