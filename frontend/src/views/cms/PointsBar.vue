<template>
  <div class="progress-wrapper is-not-native is-squared is-large">
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
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

export interface Subtask {
  max_score: number;
  fraction?: number;
  score?: number;
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
    let subtasks: Subtask[];
    if (this.subtasks === null || !this.subtasks.length)
      subtasks = [
        { max_score: this.maxScore, fraction: this.score / this.maxScore },
      ];
    else subtasks = this.subtasks;
    let cumw = 0;
    const res = [];
    const mul = 100 / this.maxScore;
    const isMoreThanHalf = [];
    for (const st of subtasks) {
      let fraction = st.fraction;
      if (st.fraction === undefined && st.score !== undefined) {
        fraction = st.score / st.max_score;
      }
      if (fraction === undefined) fraction = 0.0;
      const posWidth = fraction * st.max_score * mul;
      const negWidth = (1 - fraction) * st.max_score * mul;
      const posClass = "is-success";
      const posStart = cumw;
      const posEnd = cumw + posWidth;
      if (
        (posWidth > 0 && posEnd >= 45 && posEnd <= 55) ||
        (posWidth > 0 && posStart >= 45 && posStart <= 55) ||
        (posWidth > 0 && posStart <= 45 && posEnd >= 55)
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
        },
      );
      cumw += posWidth + negWidth;
    }
    return { isMoreThanHalf, bars: res };
  }
  get subtaskBars() {
    return this.subtaskData.bars;
  }
  get subtaskMoreThanHalfClass() {
    const v = this.subtaskData.isMoreThanHalf;
    if (!v.length) return "";
    return "is-more-than-half-success";
  }
  get scoreShow(): string {
    const a = parseFloat(this.score.toFixed(this.scorePrecision)).toString();
    if (this.showMaxScore) {
      const b = parseFloat(
        this.maxScore.toFixed(this.scorePrecision),
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
</style>
