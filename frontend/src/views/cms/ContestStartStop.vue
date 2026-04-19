<template>
  <div>
    <template v-if="isBeforeStart">
      <p>Der Wettbewerb hat noch nicht begonnen.</p>
      <p>Der Wettbewerb beginnt {{ formatToDate(contestStart) }}.</p>
    </template>
    <template v-else-if="isDuringContest">
      Der Wettbewerb hat
      <span v-if="!isContestStartDefault">{{
        formatFromDate(contestStart)
      }}</span>
      begonnen<span v-if="isContestStopDefault">.</span>
      <span v-else> und endet {{ formatToDate(contestStop) }}. </span>
    </template>
    <template v-else-if="isDuringExtraTime">
      Der Wettbewerb hat {{ formatFromDate(contestStop) }} geendet. Deine
      Extra-Zeit endet {{ formatToDate(userContestStop) }}.
    </template>
    <template v-else-if="hasAnalysis && isBeforeAnalysis">
      Der Wettbewerb hat {{ formatFromDate(contestStop) }} geendet. Die Analyse
      beginnt {{ formatToDate(analysisStart) }}.
    </template>
    <template v-else-if="hasAnalysis && isDuringAnalysis">
      Der Wettbewerb hat {{ formatFromDate(contestStop) }} geendet. Die Analyse
      hat {{ formatFromDate(analysisStart) }} begonnen<span
        v-if="isAnalysisStopDefault"
        >.</span
      >
      <span v-else> und endet {{ formatToDate(analysisStop) }}</span>
    </template>
    <template v-else-if="hasAnalysis && isAfterAnalysis">
      Die Analyse hat {{ formatFromDate(analysisStop) }} geendet.
    </template>
    <template v-else>
      Der Wettbewerb hat {{ formatFromDate(contestStop) }} geendet.
    </template>
  </div>
</template>

<script setup lang="ts">
import { Contest } from "@/types/cms";
import { computed, ref, onMounted, onUnmounted } from "vue";
import {
  formatDateLong,
  formatFromNow,
  formatToDate as formatToDateUtil,
  isAfter,
  isBefore,
} from "@/util/dt";
import { PropType } from "vue";

const props = defineProps<{ contest: Contest }>();

const now = ref<Date>(new Date());

function formatFromDate(date: Date) {
  return `${formatFromNow(now.value, date)} (${formatDateLong(date)})`;
}
function formatToDate(date: Date) {
  return `${formatToDateUtil(now.value, date)} (${formatDateLong(date)})`;
}

const contestStart = computed(() => new Date(props.contest.start));
const isContestStartDefault = computed(
  () => contestStart.value.getFullYear() === 2000,
);
const contestStop = computed(() => new Date(props.contest.stop));
const isContestStopDefault = computed(
  () => contestStop.value.getFullYear() === 2030,
);
const hasExtraTime = computed(() => props.contest.extra_time > 0);
const userContestStop = computed(
  () => new Date(contestStop.value.getTime() + props.contest.extra_time * 1000),
);
const isBeforeStart = computed(() =>
  isBefore(now.value, contestStart.value),
);
const isDuringContest = computed(() =>
  isAfter(now.value, contestStart.value) &&
  isBefore(now.value, contestStop.value),
);
const isDuringExtraTime = computed(
  () =>
    hasExtraTime.value &&
    isAfter(now.value, contestStop.value) &&
    isBefore(now.value, userContestStop.value),
);
const hasAnalysis = computed(
  () => props.contest.analysis !== null,
);
const analysisStart = computed(() =>
  props.contest.analysis === null
    ? null
    : new Date(props.contest.analysis.start),
);
const analysisStop = computed(() =>
  props.contest.analysis === null
    ? null
    : new Date(props.contest.analysis.stop),
);
const isAnalysisStopDefault = computed(
  () => analysisStop.value === null ? false : analysisStop.value.getFullYear() === 2030,
);
const isBeforeAnalysis = computed(() =>
  analysisStart.value === null ? false : isBefore(now.value, analysisStart.value),
);
const isDuringAnalysis = computed(() =>
  analysisStart.value === null || analysisStop.value === null
    ? false
    : isAfter(now.value, analysisStart.value) &&
      isBefore(now.value, analysisStop.value),
);
const isAfterAnalysis = computed(() =>
  analysisStop.value === null ? false : isAfter(now.value, analysisStop.value),
);

let nowHandle: number | null = null;

onMounted(() => {
  nowHandle = window.setInterval(() => {
    now.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  if (nowHandle !== null) clearInterval(nowHandle);
});
</script>
