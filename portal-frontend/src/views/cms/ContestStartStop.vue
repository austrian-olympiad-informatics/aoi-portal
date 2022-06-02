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
    <template v-else-if="hasAnalysis && isBeforeAnalysis">
      Der Wettbewerb hat {{ formatFromDate(contestStop) }} geendet. Die
      Analyse beginnt {{ formatToDate(analysisStart) }}.
    </template>
    <template v-else-if="hasAnalysis && isDuringAnalysis">
      Der Wettbewerb hat {{ formatFromDate(contestStop) }} geendet. Die
      Analyse hat {{ formatFromDate(analysisStart) }} begonnen<span
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

<script lang="ts">
import { Contest } from "@/types/cms";
import { Component, Prop, Vue } from "vue-property-decorator";
import {
  formatDateLong,
  formatFromNow,
  formatToDate,
  isAfter,
  isBefore,
} from "@/util/dt";
import { PropType } from "vue";

@Component
export default class ContestStartStop extends Vue {
  @Prop({
    type: Object as PropType<Contest>
  })
  contest!: Contest;
  now: Date = new Date();

  formatFromDate(date: Date) {
    return `${formatFromNow(this.now, date)} (${this.formatDate(date)})`;
  }
  formatToDate(date: Date) {
    return `${formatToDate(this.now, date)} (${this.formatDate(date)})`;
  }
  formatDate(date: Date) {
    return formatDateLong(date);
  }

  get isActive(): boolean {
    return this.contest.is_active;
  }
  get isBeforeStart(): boolean {
    return this.contestStart === null
      ? false
      : isBefore(this.now, this.contestStart);
  }
  get isDuringContest(): boolean {
    return this.contest === null
      ? false
      : isAfter(this.now, this.contestStart!) &&
          isBefore(this.now, this.contestStop!);
  }
  get isAfterContest(): boolean {
    return this.contest === null ? false : isAfter(this.now, this.contestStop!);
  }
  get hasAnalysis(): boolean {
    return this.contest !== null && this.contest.analysis !== null;
  }
  get isBeforeAnalysis(): boolean {
    return this.contest === null || this.contest.analysis === null
      ? false
      : isBefore(this.now, this.analysisStart!);
  }
  get isDuringAnalysis(): boolean {
    return this.contest === null || this.contest.analysis === null
      ? false
      : isAfter(this.now, this.analysisStart!) &&
          isBefore(this.now, this.analysisStop!);
  }
  get isAfterAnalysis(): boolean {
    return this.contest === null || this.contest.analysis === null
      ? false
      : isAfter(this.now, this.analysisStop!);
  }
  get contestStart(): Date {
    return new Date(this.contest.start);
  }
  get isContestStartDefault(): boolean {
    return this.contestStart.getFullYear() === 2000;
  }
  get contestStop(): Date {
    return new Date(this.contest.stop);
  }
  get isContestStopDefault(): boolean {
    return this.contestStop.getFullYear() === 2030;
  }
  get analysisStart(): Date | null {
    return this.contest.analysis === null
      ? null
      : new Date(this.contest.analysis.start);
  }
  get isAnalysisStartDefault(): boolean {
    return this.analysisStart === null
      ? false
      : this.analysisStart.getFullYear() === 2000;
  }
  get analysisStop(): Date | null {
    return this.contest.analysis === null
      ? null
      : new Date(this.contest.analysis.stop);
  }
  get isAnalysisStopDefault(): boolean {
    return this.analysisStop === null
      ? false
      : this.analysisStop.getFullYear() === 2030;
  }

  nowHandle: number | null = null;

  async mounted() {
    this.nowHandle = setInterval(() => {
      this.now = new Date();
    }, 1000);
  }

  destroyed() {
    if (this.nowHandle !== null)
      clearInterval(this.nowHandle);
  }
}
</script>
