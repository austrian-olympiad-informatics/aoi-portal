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

<script setup lang="ts">
import { computed } from "vue";

export interface Subtask {
  max_score: number;
  fraction?: number;
  score?: number;
}

const props = withDefaults(
  defineProps<{
    subtasks?: Subtask[] | null;
    scorePrecision?: number;
    score?: number;
    maxScore?: number;
    showMaxScore?: boolean;
  }>(),
  {
    subtasks: null,
    scorePrecision: 0,
    score: 0,
    maxScore: 0,
    showMaxScore: false,
  },
);

const subtaskData = computed(() => {
  let subtasks: Subtask[];
  if (props.subtasks === null || !props.subtasks.length)
    subtasks = [
      { max_score: props.maxScore, fraction: props.score / props.maxScore },
    ];
  else subtasks = props.subtasks;
  let cumw = 0;
  const res = [];
  const mul = 100 / props.maxScore;
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
});

const subtaskBars = computed(() => subtaskData.value.bars);

const subtaskMoreThanHalfClass = computed(() => {
  const v = subtaskData.value.isMoreThanHalf;
  if (!v.length) return "";
  return "is-more-than-half-success";
});

const scoreShow = computed((): string => {
  const a = parseFloat(props.score.toFixed(props.scorePrecision)).toString();
  if (props.showMaxScore) {
    const b = parseFloat(
      props.maxScore.toFixed(props.scorePrecision),
    ).toString();
    return `${a} / ${b}`;
  }
  return a;
});
</script>

<style scoped>
.is-grey {
  background-color: #e6e6e6 !important;
}
.is-more-than-half-success {
  color: #fff;
}
</style>
