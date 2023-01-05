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

<script lang="ts">
import cmsadmin from "@/services/cmsadmin";
import { AdminParticipationScore, AdminContestShort } from "@/types/cmsadmin";
import { Component, Prop, Vue } from "vue-property-decorator";
import PointsBar from "../PointsBar.vue";

@Component({
  components: {
    PointsBar,
  },
})
export default class AdminUserContest extends Vue {
  @Prop({
    type: Number,
  })
  userId!: number;
  @Prop({
    type: Number,
  })
  partId!: number;
  @Prop({
    type: Object,
  })
  contest!: AdminContestShort;
  scores: AdminParticipationScore | null = null;

  async mounted() {
    this.scores = await cmsadmin.getParticipationScore(this.partId);
  }

  get maxScore() {
    if (this.scores === null) return 0;

    return this.scores.tasks.reduce((acc, task) => acc + task.max_score, 0);
  }
  getTask(id: number) {
    if (this.scores === null) return null;

    return this.scores.tasks.find((task) => task.id === id);
  }
  getSubtasks(row: {
    id: number;
    subtask_scores: number[] | null;
  }) {
    return this.getTask(row.id)?.subtask_max_scores?.map((x, i) => {
      return {
        max_score: x,
        score: row.subtask_scores?.[i] || 0.0,
      };
    });
  }
}
</script>
