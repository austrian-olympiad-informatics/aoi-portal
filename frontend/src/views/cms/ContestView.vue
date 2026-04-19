<template>
  <div class="container">
    <section class="section" v-if="contest !== null">
      <h1 class="title is-2">{{ contest.description }}</h1>

      <div class="block">
        <ContestStartStop :contest="contest" />
      </div>

      <div class="block" v-if="scores !== null">
        <h2 class="title is-3">Deine Punktzahl</h2>
        <PointsBar
          :score="scores.score"
          :max-score="scores.max_score"
          :score-precision="scores.score_precision"
          :show-max-score="true"
          :subtasks="null"
        />

        <p v-if="scores.global_rank !== undefined">
          Du bist derzeit auf Rang #{{ scores.global_rank }}.
        </p>
        <p v-if="scores.points_to_next_rank !== undefined">
          Mit {{ scores.points_to_next_rank }} zusätzlichen Punkten erreichst du
          den nächsten Platz.
        </p>
      </div>

      <div class="block" v-if="contest.is_active">
        <h2 class="title is-3">Aufgaben</h2>

        <div class="columns is-multiline">
          <div
            class="column is-4"
            v-for="row in tasksWithScores"
            :key="row.task.name"
          >
            <div class="card">
              <router-link
                :to="{
                  name: 'CMSTask',
                  params: {
                    contestName: contestName,
                    taskName: row.task.name,
                  },
                }"
              >
                <div class="card-content">
                  <div class="content">
                    {{ row.task.name }} - {{ row.task.title }}

                    <PointsBar
                      v-if="row.score !== null"
                      :score="row.score.score"
                      :max-score="row.score.max_score"
                      :score-precision="row.score.score_precision"
                      :show-max-score="true"
                      :subtasks="getSubtasks(row)"
                    />
                  </div>
                </div>
              </router-link>
            </div>
          </div>
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

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import { Contest, ContestTaskScore, ContestTaskScores } from "@/types/cms";
import cms from "@/services/cms";
import CheckNotifications from "./CheckNotifications.vue";
import ContestStartStop from "./ContestStartStop.vue";
import NotificationsSection from "./NotificationsSection.vue";
import PointsBar from "./PointsBar.vue";

const route = useRoute();

const contestName = computed(() => route.params.contestName as string);
const contest = ref<Contest | null>(null);
const scores = ref<ContestTaskScores | null>(null);

async function loadContest() {
  contest.value = await cms.getContest(contestName.value);
}
async function loadScores() {
  scores.value = await cms.getContestScores(contestName.value);
}

onMounted(async () => {
  await Promise.all([loadContest(), loadScores()]);
});

const tasksWithScores = computed(() => {
  if (contest.value === null || contest.value.is_active === false) return null;
  const scoreByTask = new Map(scores.value?.tasks.map((s) => [s.task, s]));
  return contest.value.tasks.map((t) => ({
    task: t,
    score: scoreByTask.get(t.name) || null,
  }));
});

function getSubtasks(row: ContestTaskScore) {
  return row.subtask_max_scores?.map((x, i) => ({
    max_score: x,
    score: row.subtask_scores?.[i] || 0.0,
  }));
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
