<template>
  <AdminCard>
    <template v-slot:title> <b-icon icon="medal" />&nbsp;Contests </template>

    <div v-if="contests === null">
      <b-skeleton width="20%" animated></b-skeleton>
      <b-skeleton width="40%" animated></b-skeleton>
      <b-skeleton width="80%" animated></b-skeleton>
      <b-skeleton animated></b-skeleton>
    </div>

    <nav class="level" v-if="contests !== null">
      <div class="level-left">
        <div class="level-item">
          <p class="subtitle is-5">
            <strong>{{ contests.length }}</strong> Contests
          </p>
        </div>
      </div>
      <div class="level-right">
        <p class="level-item">
          <b-button icon-left="refresh" @click="reloadContestsFromCMS">
            Reload Contests from CMS
          </b-button>
        </p>
      </div>
    </nav>

    <div class="contests-container">
      <div v-for="contest in contests" :key="contest.uuid">
        <div class="card">
          <div class="card-content is-clearfix">
            <p class="title is-4 mb-3">
              {{ contest.name }}
            </p>
            <ul class="mb-2">
              <li>
                <span class="icon-text">
                  <b-icon icon="account-multiple" />&nbsp;{{
                    contest.participant_count
                  }}
                  Users
                </span>
              </li>
              <li>
                <span class="icon-text" v-if="contest.public">
                  <b-icon icon="earth" />&nbsp;Public
                </span>
                <span class="icon-text" v-else>
                  <b-icon icon="account" />&nbsp;Private
                </span>
              </li>
              <li>
                <span
                  class="icon-text"
                  v-if="contest.cms_allow_sso_authentication"
                >
                  <b-icon icon="login" />&nbsp;SSO enabled
                </span>
                <span class="icon-text" v-else>
                  <b-icon icon="login" />&nbsp;SSO disabled
                </span>
              </li>
            </ul>
            <div class="content mb-1" v-html="contest.description"></div>
            <div class="buttons is-pulled-right">
              <b-button
                tag="router-link"
                icon-left="medal"
                :to="{
                  name: 'AdminContestRanking',
                  params: { contestUuid: contest.uuid },
                }"
                >Ranking</b-button
              >
              <b-button
                tag="router-link"
                icon-left="pencil"
                :to="{
                  name: 'AdminContest',
                  params: { contestUuid: contest.uuid },
                }"
                >Edit</b-button
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { AdminContests } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import admin from "@/services/admin";

@Component({
  components: {
    AdminCard,
  },
})
export default class ContestsView extends Vue {
  contests: AdminContests | null = null;

  async loadContests() {
    this.contests = await admin.getContests();
  }

  async reloadContestsFromCMS() {
    await admin.refreshCMSContests();
    await this.loadContests();
    this.$buefy.toast.open({
      message: "Contests loaded from CMS!",
      type: "is-success",
    });
  }

  async mounted() {
    await this.loadContests();
  }
}
</script>

<style scoped>
.contests-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.icon-text {
  gap: 0.25rem;
}
</style>
