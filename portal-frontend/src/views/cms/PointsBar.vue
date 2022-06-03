<template>
  <div
    :class="{
      'progress-wrapper': true,
      'is-not-native': isSubtasks,
      'is-squared': true,
      'is-large': true,
    }"
  >
    <template v-if="!isSubtasks">
      <progress
        class="progress is-large is-squared"
        :class="{
          progress: true,
          'is-more-than-half': isMoreThanHalf,
          'is-success': score >= maxScore,
          'is-warning': score < maxScore,
        }"
        :max="maxScore"
        :value="score"
      >
        {{ scoreShow }}
      </progress>
      <p class="progress-value">{{ scoreShow }}</p>
    </template>
    <template v-else>
      <div
        v-for="(bar, index) in subtaskBars"
        class="progress-bar is-large is-squared"
        role="progressbar"
        :style="{ width: bar.width }"
        :class="bar.class"
        :key="index"
      />
      <p class="progress-value" :class="[subtaskMoreThanHalfClass]">
        {{ scoreShow }}
      </p>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

export interface Subtask {
  max_score: number;
  score_fraction: number;
}

@Component
export default class PointsBar extends Vue {
  @Prop({
    type: Array,
    default: null,
  })
  subtasks!: Subtask[] | null;

  @Prop({
    type: Number,
    default: 0,
  })
  scorePrecision!: number;

  @Prop({
    type: Number,
    default: 0,
  })
  score!: number;

  @Prop({
    type: Number,
    default: 0,
  })
  maxScore!: number;

  @Prop({
    type: Boolean,
    default: false,
  })
  showMaxScore!: boolean;

  get subtaskData() {
    if (this.subtasks === null) return { isMoreThanHalf: [], bars: [] };
    let cumw = 0;
    let res = [];
    const mul = 100 / this.maxScore;
    let isMoreThanHalf = [];
    for (const st of this.subtasks) {
      const posWidth = st.score_fraction * st.max_score * mul;
      const negWidth = (1 - st.score_fraction) * st.max_score * mul;
      const posClass = st.score_fraction >= 1 ? "is-success" : "is-warning";
      const posStart = cumw;
      const posEnd = cumw + posWidth;
      if (
        (posWidth > 0 && posEnd >= 45 && posEnd <= 55) ||
        (posStart >= 45 && posStart <= 55) ||
        (posStart <= 45 && posEnd >= 55)
      ) {
        isMoreThanHalf.push(posClass);
      }
      res.push(
        {
          width: `${posWidth}%`,
          class: ["is-success"],
        },
        {
          width: `${negWidth}%`,
          class: ["is-grey"],
        }
      );
      cumw += posWidth + negWidth;
    }
    return { isMoreThanHalf, bars: res };
  }
  get subtaskBars() {
    return this.subtaskData.bars;
  }
  get isSubtasks(): boolean {
    return this.subtasks !== null;
  }
  get isMoreThanHalf(): boolean {
    return this.score > this.maxScore / 2;
  }
  get subtaskMoreThanHalfClass() {
    const v = this.subtaskData.isMoreThanHalf;
    if (!v.length) return "";
    if (v.includes("is-success")) return "is-more-than-half-success";
    return "is-more-than-half-warning";
  }
  get scoreShow(): string {
    const a = parseFloat(this.score.toFixed(this.scorePrecision)).toString();
    if (this.showMaxScore) {
      const b = parseFloat(
        this.maxScore.toFixed(this.scorePrecision)
      ).toString();
      return `${a} / ${b}`;
    }
    return a;
  }
}
</script>

<style scoped>
.is-grey {
  background-color: #e6e6e6 !important;
}
.is-more-than-half-success {
  color: #fff;
}
.is-more-than-half-warning {
  color: rgba(0, 0, 0, 0.7);
}
</style>
