<template>
  <div class="container">
    <section class="section" v-if="contest !== null">
      <h1 class="title is-2">{{ contest.description }}</h1>

      <div class="block">
        <ContestStartStop :contest="contest" />
      </div>

      <div class="block" v-if="contest.is_active">
        <h2 class="title is-3">Aufgaben</h2>

        <div v-for="task in contest.tasks" :key="task.name">
          <router-link
            :to="{
              name: 'CMSTask',
              params: {
                contestName: contestName,
                taskName: task.name,
              },
            }"
          >
            {{ task.name }} - {{ task.title }}
          </router-link>
        </div>
      </div>

      <NotificationsSection
        :announcements="contest.announcements"
        :messages="contest.messages"
        :questions="contest.questions"
        :contest-name="contestName"
        @new-question="loadContest"
      />
    </section>
    <CheckNotifications
      :contest-name="contestName"
      @new-notification="loadContest"
    />
  </div>
</template>

<script lang="ts">
import { Contest } from "@/types/cms";
import cms from "@/services/cms";
import { Component, Vue } from "vue-property-decorator";
import CheckNotifications from "./CheckNotifications.vue";
import ContestStartStop from "./ContestStartStop.vue";
import NotificationsSection from "./NotificationsSection.vue";

@Component({
  components: {
    CheckNotifications,
    ContestStartStop,
    NotificationsSection,
  },
})
export default class ContestView extends Vue {
  get contestName(): string {
    return this.$route.params.contestName;
  }
  contest: Contest | null = null;

  async loadContest() {
    this.contest = await cms.getContest(this.contestName);
  }

  get isActive(): boolean {
    return this.contest === null ? false : this.contest.is_active;
  }

  async mounted() {
    await this.loadContest();
  }
}
</script>

<style scoped>
.question-reply {
  border-top: 1px solid #3e8ed085;
  margin-top: 10px;
  padding-top: 10px;
}
.notification-text {
  white-space: pre-line;
}
.question-form {
  margin-bottom: 1.5rem;
  padding: 19px;
  background-color: #f5f5f5;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}
</style>
