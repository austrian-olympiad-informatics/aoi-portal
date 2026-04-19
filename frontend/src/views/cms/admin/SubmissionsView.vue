<template>
  <div
    class="wrap"
    :class="[selectedSub !== null ? 'has-selection' : undefined]"
  >
    <div class="left-column">
      <div class="left-wrap">
        <h1 class="title is-3">Einsendungen</h1>
        <b-breadcrumb align="is-left" size="is-left">
          <b-breadcrumb-item tag="router-link" :to="{ name: 'CMSAdminIndex' }">
            Admin Panel
          </b-breadcrumb-item>
          <b-breadcrumb-item tag="router-link" :to="$route.fullPath" active>
            Submissions
          </b-breadcrumb-item>
        </b-breadcrumb>

        <div class="block">
          <form>
            <b-field label="Filter by Contest">
              <SimpleAutoselect
                :data="contests"
                :loading="contests === null"
                v-model="filterByContestId"
                :value-func="(c) => c.id"
                :formatter="(c) => c.description"
                @input="reloadSubmissions"
              />
            </b-field>
            <b-field label="Filter by Task">
              <SimpleAutoselect
                :data="filteredTasks"
                :loading="tasks === null"
                v-model="filterByTaskId"
                :value-func="(t) => t.id"
                :formatter="
                  (t) =>
                    `${t.name} - ${t.title} (${
                      t.contest ? t.contest.description : 'No Contest'
                    })`
                "
                @input="reloadSubmissions"
              />
            </b-field>
            <b-field label="Filter by User">
              <SimpleAutoselect
                :data="filteredUsers"
                :loading="users === null"
                v-model="filterByUserId"
                :value-func="(u) => u.id"
                :formatter="
                  (u) => `${u.first_name} ${u.last_name} (${u.username})`
                "
                @input="reloadSubmissions"
              />
            </b-field>
          </form>
        </div>

        <div class="block">
          <nav class="level">
            <div class="level-left">
              <div class="level-item">
                <p class="subtitle is-5">
                  <strong>{{ total }}</strong> submissions
                </p>
              </div>
            </div>

            <div class="level-right">
              <div class="level-item">
                <b-button icon-left="reload" @click="reloadSubmissions">
                  Reload
                </b-button>
              </div>
            </div>
          </nav>
          <b-table
            :data="submissions"
            :loading="loading"
            paginated
            backend-pagination
            :total="total"
            :per-page="perPage"
            @page-change="onPageChange"
            narrowed
            :selected="selectedSub"
            @click="onRowClick"
            focusable
            scrollable
            custom-row-key="uuid"
            :mobile-cards="false"
          >
            <b-table-column
              label="Datum"
              width="0.1%"
              :th-attrs="nowrapAttrs"
              :td-attrs="nowrapAttrs"
              v-slot="props"
            >
              {{ formatSubDate(new Date(props.row.timestamp)) }}
            </b-table-column>
            <b-table-column
              label="Contest"
              width="0.1%"
              :th-attrs="nowrapAttrs"
              :td-attrs="nowrapAttrs"
              v-slot="props"
              :visible="filterByContestId === null && filterByTaskId === null"
            >
              <router-link
                :to="{
                  name: 'CMSAdminContest',
                  params: { contestId: props.row.contest.id },
                }"
              >
                {{ props.row.contest.description }}
              </router-link>
            </b-table-column>
            <b-table-column
              label="User"
              width="0.1%"
              :th-attrs="nowrapAttrs"
              :td-attrs="nowrapAttrs"
              v-slot="props"
              :visible="filterByUserId === null"
            >
              <router-link
                :to="{
                  name: 'CMSAdminUser',
                  params: { userId: props.row.participation.user.id },
                }"
              >
                {{ formatPart(props.row.participation) }}
              </router-link>
            </b-table-column>
            <b-table-column
              label="Task"
              width="0.1%"
              :th-attrs="nowrapAttrs"
              :td-attrs="nowrapAttrs"
              v-slot="props"
              :visible="filterByTaskId === null"
            >
              <router-link
                :to="{
                  name: 'CMSAdminTask',
                  params: { taskId: props.row.task.id },
                }"
              >
                {{ props.row.task.name }}
              </router-link>
            </b-table-column>
            <b-table-column label="Punktzahl" v-slot="props" centered>
              <template v-if="props.row.result.status === 'scored'">
                <PointsBar
                  :subtasks="props.row.result.subtasks"
                  :score="props.row.result.score"
                  :max-score="props.row.max_score"
                  :score-precision="props.row.result.score_precision"
                />
              </template>
              <template
                v-else-if="props.row.result.status === 'compilation_failed'"
              >
                <i>Kompilierung fehlgeschlagen</i>
              </template>
              <template v-else>
                <i>{{
                  {
                    compiling: "Kompilierung...",
                    evaluating: "Auswertung...",
                    scoring: "Bewertung...",
                  }[props.row.result.status]
                }}</i>
                <span class="sub-loading"></span>
              </template>
            </b-table-column>
          </b-table>
        </div>
      </div>
    </div>
    <div class="right-column">
      <router-view class="right-wrap" :key="$route.fullPath" />
    </div>
  </div>
</template>

<script setup lang="ts">
import cmsadmin from "@/services/cmsadmin";
import {
  AdminSubmissionsPaginated,
  AdminParticipationShort,
  AdminSubmissionShort,
  AdminContests,
  AdminUsers,
  AdminAllTasks,
} from "@/types/cmsadmin";
import { formatDateShort } from "@/util/dt";
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import PointsBar from "../PointsBar.vue";
import SimpleAutoselect from "./SimpleAutoselect.vue";

const route = useRoute();
const router = useRouter();

const data = ref<AdminSubmissionsPaginated | null>(null);
const loading = ref(true);
const perPage = ref(50);
const page = ref(1);

const submissions = computed<AdminSubmissionShort[]>(() =>
  data.value === null ? [] : data.value.items,
);
const total = computed<number | null>(() =>
  data.value === null ? null : data.value.total,
);

const contests = ref<AdminContests | null>(null);
const users = ref<AdminUsers | null>(null);
const tasks = ref<AdminAllTasks | null>(null);

const filterByContestId = ref<number | null>(null);
const filterByTaskId = ref<number | null>(null);
const filterByUserId = ref<number | null>(null);

const filteredTasks = computed(() => {
  if (tasks.value === null) return null;
  if (filterByContestId.value === null) return tasks.value;
  return tasks.value.filter((t) => t.contest?.id === filterByContestId.value);
});

const filteredUsers = computed(() => {
  if (users.value === null) return null;
  if (filterByContestId.value === null) return users.value;
  return users.value.filter((u) =>
    u.participations.some((p) => p.contest.id === filterByContestId.value),
  );
});

const selectedSub = ref<{ uuid: string } | null>(null);

async function onPageChange(idx: number) {
  page.value = idx;
  await reloadSubmissions();
}

async function loadSubmissions() {
  data.value = await cmsadmin.getSubmissions({
    page: page.value,
    perPage: perPage.value,
    contestId:
      filterByContestId.value === null ? undefined : filterByContestId.value,
    taskId: filterByTaskId.value === null ? undefined : filterByTaskId.value,
    userId: filterByUserId.value === null ? undefined : filterByUserId.value,
  });
}

async function reloadSubmissions() {
  router.push({
    path: route.path,
    query: {
      ...route.query,
      page: page.value.toString(),
      contest_id: filterByContestId.value?.toString(),
      task_id: filterByTaskId.value?.toString(),
      user_id: filterByUserId.value?.toString(),
    },
  });
  loading.value = true;
  await loadSubmissions();
  loading.value = false;
}

async function loadContests() {
  contests.value = await cmsadmin.getContests();
}
async function loadTasks() {
  tasks.value = await cmsadmin.getTasks();
}
async function loadUsers() {
  users.value = await cmsadmin.getUsers();
}

let reloadHandle: number | null = null;

onUnmounted(() => {
  if (reloadHandle !== null) clearInterval(reloadHandle);
});

onMounted(async () => {
  if (route.query.contest_id !== undefined)
    filterByContestId.value = +(route.query.contest_id as string);
  if (route.query.task_id !== undefined)
    filterByTaskId.value = +(route.query.task_id as string);
  if (route.query.user_id !== undefined)
    filterByUserId.value = +(route.query.user_id as string);
  if (route.params.submissionUuid !== undefined)
    selectedSub.value = { uuid: route.params.submissionUuid as string };
  reloadHandle = window.setInterval(async () => {
    await loadSubmissions();
  }, 15000);
  await Promise.all([
    loadSubmissions(),
    loadContests(),
    loadTasks(),
    loadUsers(),
  ]);
  loading.value = false;
});

function formatPart(part: AdminParticipationShort) {
  return `${part.user.first_name} ${part.user.last_name}`;
}

function formatSubDate(date: Date) {
  return formatDateShort(new Date(), date);
}

function onRowClick(v: { uuid: string }) {
  if (selectedSub.value?.uuid === v.uuid) {
    selectedSub.value = null;
    router.push({
      name: "CMSAdminSubmissions",
      query: route.query,
    });
    return;
  }
  selectedSub.value = v;
  router.push({
    name: "CMSAdminSubmission",
    params: {
      submissionUuid: v.uuid,
    },
    query: route.query,
  });
}

function nowrapAttrs() {
  return {
    style: {
      "white-space": "nowrap",
    },
  };
}

watch(
  () => route.params.submissionUuid,
  (uuid) => {
    selectedSub.value =
      uuid !== undefined ? { uuid: uuid as string } : null;
  },
);
</script>

<style lang="scss" scoped>
@import "~bulma/sass/utilities/mixins";

.wrap {
  display: flex;
  flex-direction: row;
  height: 100%;
}
.left-column {
  flex: none;
  width: 40%;
  display: flex;
  max-width: 640px;
  flex-direction: column;
  border-right: 2px solid rgb(207, 207, 207);
}
.left-wrap {
  flex-basis: 0;
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
}
.right-column {
  flex-grow: 1;
  flex-shrink: 0;
  flex-basis: auto;
  width: 60%;
  display: flex;
  flex-direction: column;
}
.right-wrap {
  flex-basis: 0;
  flex-grow: 1;
  overflow-y: auto;
}

@include touch {
  .wrap {
    flex-direction: column;
  }
  .left-column {
    width: 100%;
    max-width: initial;
    min-width: initial;
  }
  .left-wrap {
    overflow-y: initial;
  }
  .right-column {
    width: 100%;
    height: auto;
    flex: initial;
    /* prevent layout jumping around when selecting a submission */
    min-height: 80vh;
  }
  .has-selection .left-wrap {
    display: none;
  }
  .has-selection .right-column {
    height: 100%;
  }
}
</style>
