<template>
  <div>
    <h3 class="title is-4">{{ contest.description }}</h3>

    <div class="block" v-if="scores !== null">
      <router-link
        :to="{
          name: 'CMSAdminSubmissions',
          query: { user_id: userId, contest_id: contest.id },
        }"
      >
        <PointsBar
          :score="scores.score"
          :max-score="maxScore"
          :score-precision="scores.score_precision"
          :show-max-score="true"
          :subtasks="null"
        />
      </router-link>

      <span v-if="!scores.hidden"> Derzeit auf Rang #{{ scores.rank }}. </span>
    </div>

    <div class="block" v-if="scores !== null">
      <div class="columns is-multiline">
        <div
          class="column is-4"
          v-for="row in scores.task_scores"
          :key="row.id"
        >
          <div class="card">
            <router-link
              :to="{
                name: 'CMSAdminSubmissions',
                query: {
                  user_id: userId,
                  task_id: row.id,
                  contest_id: contest.id,
                },
              }"
            >
              <div class="card-content">
                <div class="content">
                  {{ getTask(row.id).name }} - {{ getTask(row.id).title }}

                  <PointsBar
                    :score="row.score"
                    :max-score="getTask(row.id).max_score"
                    :score-precision="getTask(row.id).score_precision"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import cmsadmin from "@/services/cmsadmin";
import { AdminParticipationScore, AdminContestShort } from "@/types/cmsadmin";
import PointsBar from "../PointsBar.vue";

const props = defineProps<{
  userId: number;
  partId: number;
  contest: AdminContestShort;
}>();

const scores = ref<AdminParticipationScore | null>(null);

onMounted(async () => {
  scores.value = await cmsadmin.getParticipationScore(props.partId);
});

const maxScore = computed(() => {
  if (scores.value === null) return 0;
  return scores.value.tasks.reduce((acc, task) => acc + task.max_score, 0);
});

function getTask(id: number) {
  if (scores.value === null) return null;
  return scores.value.tasks.find((task) => task.id === id);
}

function getSubtasks(row: { id: number; subtask_scores: number[] | null }) {
  return getTask(row.id)?.subtask_max_scores?.map((x, i) => ({
    max_score: x,
    score: row.subtask_scores?.[i] || 0.0,
  }));
}
</script>
