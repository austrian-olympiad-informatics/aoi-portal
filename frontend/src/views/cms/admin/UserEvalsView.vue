<template>
  <div
    class="wrap"
    :class="[selectedUserEval !== null ? 'has-selection' : undefined]"
  >
    <div class="left-column">
      <div class="left-wrap">
        <h1 class="title is-3">User Evals</h1>
        <b-breadcrumb align="is-left" size="is-left">
          <b-breadcrumb-item tag="router-link" :to="{ name: 'CMSAdminIndex' }">
            Admin Panel
          </b-breadcrumb-item>
          <b-breadcrumb-item tag="router-link" :to="$route.fullPath" active>
            User Evals
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
                @input="reloadUserEvals"
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
                @input="reloadUserEvals"
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
                @input="reloadUserEvals"
              />
            </b-field>
          </form>
        </div>

        <div class="block">
          <nav class="level">
            <div class="level-left">
              <div class="level-item">
                <p class="subtitle is-5">
                  <strong>{{ total }}</strong> user evals
                </p>
              </div>
            </div>

            <div class="level-right">
              <div class="level-item">
                <b-button icon-left="reload" @click="reloadUserEvals">
                  Reload
                </b-button>
              </div>
            </div>
          </nav>
          <b-table
            :data="userEvals"
            :loading="loading"
            paginated
            backend-pagination
            :total="total"
            :per-page="perPage"
            @page-change="onPageChange"
            narrowed
            :selected="selectedUserEval"
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
            <b-table-column label="Status" v-slot="props" centered>
              <template v-if="props.row.result.status === 'evaluated'">
                <i>Ausgewertet</i>
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
  AdminParticipationShort,
  AdminContests,
  AdminUsers,
  AdminAllTasks,
  AdminUserEvalsPaginated,
  AdminUserEvalShort,
} from "@/types/cmsadmin";
import { formatDateShort } from "@/util/dt";
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import SimpleAutoselect from "./SimpleAutoselect.vue";

const route = useRoute();
const router = useRouter();

const data = ref<AdminUserEvalsPaginated | null>(null);
const loading = ref(true);
const perPage = ref(50);
const page = ref(1);

const userEvals = computed<AdminUserEvalShort[]>(() =>
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

const selectedUserEval = ref<{ uuid: string } | null>(null);

async function onPageChange(idx: number) {
  page.value = idx;
  await reloadUserEvals();
}

async function loadUserEvals() {
  data.value = await cmsadmin.getUserEvals({
    page: page.value,
    perPage: perPage.value,
    contestId:
      filterByContestId.value === null ? undefined : filterByContestId.value,
    taskId: filterByTaskId.value === null ? undefined : filterByTaskId.value,
    userId: filterByUserId.value === null ? undefined : filterByUserId.value,
  });
}

async function reloadUserEvals() {
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
  await loadUserEvals();
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
  if (route.params.userEvalUuid !== undefined)
    selectedUserEval.value = { uuid: route.params.userEvalUuid as string };
  reloadHandle = window.setInterval(async () => {
    await loadUserEvals();
  }, 15000);
  await Promise.all([
    loadUserEvals(),
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
  if (selectedUserEval.value?.uuid === v.uuid) {
    selectedUserEval.value = null;
    router.push({
      name: "CMSAdminUserEvals",
      query: route.query,
    });
    return;
  }
  selectedUserEval.value = v;
  router.push({
    name: "CMSAdminUserEval",
    params: {
      userEvalUuid: v.uuid,
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
  () => route.params.userEvalUuid,
  (uuid) => {
    selectedUserEval.value =
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
  }
  .has-selection .left-wrap {
    display: none;
  }
  .has-selection .right-column {
    height: 100%;
  }
}
</style>
