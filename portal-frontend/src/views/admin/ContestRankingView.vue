<template>
  <div>
    <h1 class="title" v-if="contest !== null">
      Ranking for {{ contest.name }}
    </h1>
    <div v-if="contest === null || ranking === null">
      <b-skeleton width="20%" animated></b-skeleton>
      <b-skeleton width="40%" animated></b-skeleton>
      <b-skeleton width="80%" animated></b-skeleton>
      <b-skeleton animated></b-skeleton>
    </div>

    <div v-if="contest !== null && ranking !== null">
      <b-table
        :data="tableData"
        :default-sort="['total_score', 'desc']"
        default-sort-direction="desc"
        hoverable
        :mobile-cards="false"
      >
        <b-table-column label="User" v-slot="props" sticky>
          <router-link
            :to="{
              name: 'AdminUser',
              params: { userId: props.row.user_id },
            }"
          >
            {{ props.row.user_first_name }} {{ props.row.user_last_name }} ({{
              props.row.user_username
            }})
          </router-link>
        </b-table-column>
        <b-table-column
          v-for="task in ranking.tasks"
          :key="task"
          :label="task"
          v-slot="props"
          numeric
          sortable
          :field="`task_scores.${task}`"
        >
          {{ props.row.task_scores[task] }}
        </b-table-column>
        <b-table-column
          label="Total Score"
          v-slot="props"
          numeric
          sortable
          field="total_score"
        >
          {{ props.row.total_score }}
        </b-table-column>
      </b-table>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import admin from "@/services/admin";
import { AdminContestDetail, AdminContestRanking } from "@/types/admin";

interface TableRow {
  user_id: number;
  user_username: string;
  user_first_name: string;
  user_last_name: string;
  part_id: number;
  part_cmsid: number;
  task_scores: {
    [key: string]: number;
  };
  total_score: number;
}

@Component({
  components: {},
})
export default class ContestView extends Vue {
  contestUuid!: string;
  contest: AdminContestDetail | null = null;
  ranking: AdminContestRanking | null = null;

  async mounted() {
    this.contestUuid = this.$route.params.contestUuid;
    await Promise.all([this.loadContest(), this.loadRanking()]);
  }

  async loadContest() {
    this.contest = await admin.getContest(this.contestUuid);
  }
  async loadRanking() {
    this.ranking = await admin.getContestRanking(this.contestUuid);
  }

  get tableData(): TableRow[] {
    if (this.contest === null || this.ranking === null) return [];
    const uidToRanking = new Map(
      this.ranking.ranking.map((r) => [r.user_id, r])
    );
    const taskScores = this.ranking.tasks.reduce((acc, v) => {
      return {...acc, [v]: 0.0};
    }, {});
    return this.contest.participations.map((p) => {
      const v = uidToRanking.get(p.user.id);
      const taskScores = this.ranking!.tasks.reduce((acc, k) => {
        return {...acc, [k]: v?.task_scores[k] || 0.0};
      }, {});
      return {
        user_id: p.user.id,
        user_username: p.user.username,
        user_first_name: p.user.first_name,
        user_last_name: p.user.last_name,
        part_id: p.id,
        part_cmsid: p.cms_id,
        task_scores: taskScores,
        total_score: v?.total_score || 0.0,
      };
    });
  }
}
</script>
