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

<script lang="ts">
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
import { Component, Vue, Watch } from "vue-property-decorator";
import SimpleAutoselect from "./SimpleAutoselect.vue";

@Component({
  components: {
    SimpleAutoselect,
  },
})
export default class AdminUserEvalsView extends Vue {
  data: AdminUserEvalsPaginated | null = null;
  loading = true;
  get userEvals(): AdminUserEvalShort[] {
    return this.data === null ? [] : this.data.items;
  }
  get total(): number | null {
    return this.data === null ? null : this.data.total;
  }
  perPage = 50;
  page = 1;

  contests: AdminContests | null = null;
  users: AdminUsers | null = null;
  tasks: AdminAllTasks | null = null;

  filterByContestId: number | null = null;
  filterByTaskId: number | null = null;
  filterByUserId: number | null = null;

  async onPageChange(idx: number) {
    this.page = idx;
    await this.reloadUserEvals();
  }

  async loadUserEvals() {
    this.data = await cmsadmin.getUserEvals({
      page: this.page,
      perPage: this.perPage,
      contestId:
        this.filterByContestId === null ? undefined : this.filterByContestId,
      taskId: this.filterByTaskId === null ? undefined : this.filterByTaskId,
      userId: this.filterByUserId === null ? undefined : this.filterByUserId,
    });
  }
  async reloadUserEvals() {
    this.$router.push({
      path: this.$route.path,
      query: {
        ...this.$route.query,
        page: this.page.toString(),
        contest_id: this.filterByContestId?.toString(),
        task_id: this.filterByTaskId?.toString(),
        user_id: this.filterByUserId?.toString(),
      },
    });
    this.loading = true;
    await this.loadUserEvals();
    this.loading = false;
  }
  async loadContests() {
    this.contests = await cmsadmin.getContests();
  }
  async loadTasks() {
    this.tasks = await cmsadmin.getTasks();
  }
  get filteredTasks() {
    if (this.tasks === null) return null;
    if (this.filterByContestId === null) return this.tasks;
    return this.tasks.filter((t) => t.contest?.id === this.filterByContestId);
  }
  async loadUsers() {
    this.users = await cmsadmin.getUsers();
  }
  get filteredUsers() {
    if (this.users === null) return null;
    if (this.filterByContestId === null) return this.users;
    return this.users.filter((u) =>
      u.participations.some((p) => p.contest.id === this.filterByContestId),
    );
  }
  reloadHandle: number | null = null;
  destroyed() {
    if (this.reloadHandle !== null) clearInterval(this.reloadHandle);
  }

  async mounted() {
    if (this.$route.query.contest_id !== undefined)
      this.filterByContestId = +this.$route.query.contest_id;
    if (this.$route.query.task_id !== undefined)
      this.filterByTaskId = +this.$route.query.task_id;
    if (this.$route.query.user_id !== undefined)
      this.filterByUserId = +this.$route.query.user_id;
    if (this.$route.params.userEvalUuid !== undefined)
      this.selectedUserEval = { uuid: this.$route.params.userEvalUuid };
    this.reloadHandle = window.setInterval(async () => {
      await this.loadUserEvals();
    }, 15000);
    await Promise.all([
      this.loadUserEvals(),
      this.loadContests(),
      this.loadTasks(),
      this.loadUsers(),
    ]);
    this.loading = false;
  }

  formatPart(part: AdminParticipationShort) {
    return `${part.user.first_name} ${part.user.last_name}`;
  }

  formatSubDate(date: Date) {
    return formatDateShort(new Date(), date);
  }

  selectedUserEval: { uuid: string } | null = null;
  onRowClick(v: { uuid: string }) {
    if (this.selectedUserEval?.uuid === v.uuid) {
      this.selectedUserEval = null;
      this.$router.push({
        name: "CMSAdminUserEvals",
        query: this.$route.query,
      });
      return;
    }
    this.selectedUserEval = v;
    this.$router.push({
      name: "CMSAdminUserEval",
      params: {
        userEvalUuid: v.uuid,
      },
      query: this.$route.query,
    });
  }

  nowrapAttrs() {
    return {
      style: {
        "white-space": "nowrap",
      },
    };
  }

  @Watch("$route")
  watchRoute() {
    if (this.$route.params.userEvalUuid !== undefined)
      this.selectedUserEval = { uuid: this.$route.params.userEvalUuid };
    else this.selectedUserEval = null;
  }
}
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
