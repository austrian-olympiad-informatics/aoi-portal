<template>
  <div class="card">
    <div class="card-content is-clearfix">
      <p class="title is-4 mb-3">
        {{ contest.name }}
      </p>
      <div class="content mb-1">
        {{ contest.description }}

        <template v-if="contest.joined && contest.sso_enabled">
          <b-button
            tag="router-link"
            icon-right="chevron-right"
            class="is-pulled-right"
            :to="{
              name: 'ContestSSO',
              params: { contestUuid: contest.uuid },
            }"
            >Zum Server</b-button
          >
        </template>
        <template v-if="contest.joined && !contest.sso_enabled">
          <b-button
            tag="a"
            icon-right="chevron-right"
            class="is-pulled-right"
            :href="contest.url"
            >Zum Server</b-button
          >
        </template>
        <template v-if="!contest.joined && contest.can_join">
          <b-button
            icon-right="chevron-right"
            class="is-pulled-right"
            @click="joinContest"
            >Teilnehmen</b-button
          >
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import contests from "@/services/contests";
import { PropType } from "vue";
import { Contest } from "@/types/contests";

@Component
export default class ContestCard extends Vue {
  @Prop({
    type: Object as PropType<Contest>,
  })
  contest!: Contest;

  async joinContest() {
    await contests.joinContest(this.contest.uuid);
    this.$emit("joined");
  }
}
</script>
