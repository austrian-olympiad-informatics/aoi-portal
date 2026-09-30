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
            <strong>{{ visibleContests.length }}</strong> Contests
          </p>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <span class="mr-2">Sort:</span>
          <div class="buttons has-addons">
            <b-button
              :type="sortOrder === 'id' ? 'is-primary' : undefined"
              @click="sortOrder = 'id'"
            >
              ID
            </b-button>
            <b-button
              :type="sortOrder === 'name' ? 'is-primary' : undefined"
              @click="sortOrder = 'name'"
            >
              Name
            </b-button>
            <b-button
              :type="sortOrder === 'priority' ? 'is-primary' : undefined"
              @click="sortOrder = 'priority'"
            >
              Priority
            </b-button>
          </div>
        </div>
        <p class="level-item">
          <b-switch v-model="hideDeleted">Hide Deleted Contests</b-switch>
        </p>
        <p class="level-item">
          <b-button icon-left="refresh" @click="reloadContestsFromCMS">
            Reload Contests from CMS
          </b-button>
        </p>
      </div>
    </nav>

    <div class="contests-container">
      <div v-for="contest in visibleContests" :key="contest.uuid">
        <div class="card">
          <div class="card-content is-clearfix">
            <b-tag
              v-if="contest.deleted"
              class="deleted-badge"
              type="is-light"
              rounded
            >
              Deleted
            </b-tag>
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
                <span class="icon-text" v-if="contest.open_signup">
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
                v-if="!contest.deleted"
                tag="router-link"
                icon-left="medal"
                :to="{
                  name: 'CMSAdminContest',
                  params: { contestId: contest.cms_id },
                }"
                >Info</b-button
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

<script setup lang="ts">
import { computed, ref } from "vue";
import { onMounted } from "vue";
import { useToast } from "buefy";
import { AdminContests } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import admin from "@/services/admin";

const toast = useToast();

type SortOrder = "id" | "name" | "priority";

const contests = ref<AdminContests | null>(null);
const hideDeleted = ref(true);
const sortOrder = ref<SortOrder>("id");

const visibleContests = computed<AdminContests>(() => {
  if (contests.value === null) return [];
  const filtered = hideDeleted.value
    ? contests.value.filter((c) => !c.deleted)
    : contests.value;
  return [...filtered].sort((a, b) => {
    switch (sortOrder.value) {
      case "id":
        return a.id - b.id;
      case "name":
        return a.name.localeCompare(b.name, undefined, { sensitivity: "base" });
      case "priority":
        return b.order_priority - a.order_priority;
      default:
        return 0;
    }
  });
});

async function loadContests() {
  contests.value = await admin.getContests();
}

async function reloadContestsFromCMS() {
  await admin.refreshCMSContests();
  await loadContests();
  toast.open({
    message: "Contests loaded from CMS!",
    type: "is-success",
  });
}

onMounted(async () => {
  await loadContests();
});
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
.card-content {
  position: relative;
}
.deleted-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: hsl(0, 0%, 48%);
}
</style>
