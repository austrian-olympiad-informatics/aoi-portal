<template>
  <div class="wrapper">
    <nav class="breadcrumb" aria-label="breadcrumbs">
      <ul>
        <li>
          <router-link :to="{ name: 'Home' }">Home</router-link>
        </li>
        <li>
          <router-link :to="{ name: 'CMSContest', params: { contestName } }">
            {{ task.contest.description }}
          </router-link>
        </li>
        <li class="is-active">
          <router-link
            :to="{ name: 'CMSTask', params: { contestName, taskName } }"
            aria-current="page"
          >
            {{ taskName }}
          </router-link>
        </li>
      </ul>
    </nav>
    <h1 class="title">{{ task.name }} - {{ task.title }}</h1>

    <div class="block">
      <h2 class="title is-4">Deine Punktzahl</h2>
      <PointsBar
        :score="task.score"
        :max-score="task.max_score"
        :score-precision="task.score_precision"
        :show-max-score="true"
        :subtasks="taskScoreSubtasks"
      />
    </div>

    <div class="block submissions-block">
      <h2 class="title is-4">Deine Einsendungen</h2>
      <div v-if="task.submissions.length">
        <table class="table is-fullwidth">
          <thead>
            <tr>
              <th class="date-td">Datum</th>
              <th>Punktzahl</th>
            </tr>
          </thead>
          <TransitionGroup tag="tbody" name="submission-list">
            <router-link
              v-for="sub in sortedSubmissions"
              :key="sub.uuid"
              :to="{
                name: 'CMSSubmissionDetails',
                params: {
                  contestName: contestName,
                  taskName: taskName,
                  submissionUuid: sub.uuid,
                },
              }"
              custom
              v-slot="{ navigate, isActive }"
            >
              <tr
                :class="{
                  'is-clickable': true,
                  'is-active': isActive,
                }"
                @click="
                  (event) =>
                    isActive
                      ? showCodePanel()
                      : navgiateSubmission(event, navigate)
                "
              >
                <td class="date-td">
                  {{ formatSubDate(new Date(sub.timestamp)) }}
                </td>
                <td v-if="sub.result.status === 'scored'">
                  <PointsBar
                    :subtasks="sub.result.subtasks"
                    :score="sub.result.score"
                    :max-score="task.max_score"
                    :score-precision="task.score_precision"
                  />
                </td>
                <td
                  class="has-text-centered"
                  v-else-if="sub.result.status === 'compilation_failed'"
                >
                  <i>Kompilierung fehlgeschlagen</i>
                </td>

                <td class="has-text-centered" v-else>
                  <i>{{
                    {
                      compiling: "Kompilierung...",
                      evaluating: "Auswertung...",
                      scoring: "Bewertung...",
                    }[sub.result.status]
                  }}</i>
                  <span class="sub-loading"></span>
                </td>
              </tr>
            </router-link>
          </TransitionGroup>
        </table>
      </div>
      <div v-else>Noch keine Einsendungen.</div>
    </div>

    <div class="block" v-if="task.statements.length">
      <h2 class="title is-4">Problemstellung</h2>
      <div>
        <template v-if="task.statements.length === 1">
          <b-button
            type="is-primary"
            @click="downloadStatement(task.statements[0])"
          >
            Problemstellung herunterladen ({{
              task.statements[0].language.toUpperCase()
            }})
          </b-button>
        </template>
        <template v-else>
          <b-dropdown aria-role="list">
            <template #trigger="{ active }">
              <b-button
                label="Problemstellung herunterladen"
                type="is-primary"
                :icon-right="active ? 'menu-up' : 'menu-down'"
              />
            </template>
            <b-dropdown-item
              v-for="stat in task.statements"
              :key="stat.language"
              @click="downloadStatement(stat)"
            >
              {{ stat.language.toUpperCase() }}
            </b-dropdown-item>
          </b-dropdown>
        </template>
      </div>
    </div>

    <div class="block" v-if="statement_html !== null">
      <div class="content" ref="statementHtml" v-html="statement_html" />
    </div>

    <div class="block" v-if="task.attachments.length">
      <h2 class="title is-4">Anhänge</h2>
      <div>
        <div v-for="att in task.attachments" :key="att.filename">
          <b-button type="is-primary" @click="downloadAttachment(att)">
            {{ att.filename }}
          </b-button>
        </div>
      </div>
    </div>
    <div class="block">
      <table>
        <tbody>
          <tr v-if="task.time_limit !== null">
            <td class="pr-5">
              <span class="icon-text">
                <b-icon icon="timer-outline" />
                <span><b>Zeitlimit</b></span>
              </span>
            </td>
            <td>{{ task.time_limit }} s</td>
          </tr>
          <tr v-if="task.memory_limit !== null">
            <td class="pr-5">
              <span class="icon-text">
                <b-icon icon="memory" />
                <span><b>Speicherlimit</b></span>
              </span>
            </td>
            <td>{{ task.memory_limit / (1024 * 1024) }} MiB</td>
          </tr>
        </tbody>
      </table>
    </div>

    <NotificationsSection
      :announcements="task.announcements"
      :messages="task.messages"
      :questions="task.questions"
      :contest-name="contestName"
      :task-name="taskName"
      @new-question="$emit('reload-task')"
    />
  </div>
</template>

<script lang="ts">
import { SubmissionShort, Task } from "@/types/cms";
import cms from "@/services/cms";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { formatDateShort } from "@/util/dt";
import { PropType } from "vue";
import { downloadBlob } from "@/util/download";
import PointsBar from "./PointsBar.vue";
import NotificationsSection from "./NotificationsSection.vue";
import katex from 'katex';

@Component({
  components: {
    PointsBar,
    NotificationsSection,
  },
})
export default class DescriptionPanel extends Vue {
  @Prop({
    type: Object as PropType<Task>,
  })
  task!: Task;
  statement_html: string | null = null;

  get contestName(): string {
    return this.$route.params.contestName;
  }
  get taskName(): string {
    return this.$route.params.taskName;
  }
  get sortedSubmissions(): SubmissionShort[] {
    return this.task.submissions.sort((a, b) => {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
  }
  get taskScoreSubtasks() {
    // reassemble score subtasks in submission subtasks format
    if (this.task.scoring.type === "sum") return null;
    const ourSt = this.task.score_subtasks!;
    const maxSt = this.task.scoring.subtasks;
    return maxSt.map((x, i) => {
      return {
        max_score: x,
        fraction: i < ourSt.length ? ourSt[i].fraction : 0,
      };
    });
  }

  now: Date = new Date();

  async downloadStatement(st: { language: string; digest: string }) {
    const resp = await cms.getStatement(
      this.contestName!,
      this.taskName!,
      st.language,
      st.digest
    );
    downloadBlob(resp, `${this.taskName} (${st.language.toUpperCase()}).pdf`);
  }
  async downloadAttachment(att: { filename: string; digest: string }) {
    const resp = await cms.getAttachment(
      this.contestName!,
      this.taskName!,
      att.filename,
      att.digest
    );
    downloadBlob(resp, att.filename);
  }
  async mounted() {
    this.now = new Date();
    this.scheduleCheckSubmissions(1000);
    if (this.task.statement_html_digest !== null) {
      this.statement_html = await (await cms.getStatementHTML(this.contestName!, this.taskName!, this.task.statement_html_digest)).text();
      this.$nextTick(() => {
        const root = this.$refs.statementHtml as Element;
        const mathElems = root.querySelectorAll(".math");
        const macros = {};
        mathElems.forEach((elem) => {
          const displayMode = elem.classList.contains("display");
          const text = elem.textContent;
          katex.render(text, elem, {
              throwOnError: false,
              displayMode: displayMode,
              macros
          });
        })
      });
    }
  }

  formatSubDate(date: Date) {
    return formatDateShort(this.now!, date);
  }

  navgiateSubmission(event: any, navigate: any) {
    navigate(event);
    this.$emit("show-submission");
  }

  get pendingSubmissions(): SubmissionShort[] {
    return this.task.submissions.filter((sub) =>
      ["compiling", "evaluating", "scoring"].includes(sub.result.status)
    );
  }
  get hasPendingSubmissions(): boolean {
    return this.pendingSubmissions.length > 0;
  }
  get subStates(): string[] {
    return this.task.submissions.map((sub) => sub.result.status);
  }

  checkSubTimeout: number | null = null;

  scheduleCheckSubmissions(timeout: number) {
    if (this.checkSubTimeout !== null) clearTimeout(this.checkSubTimeout);
    this.checkSubTimeout = setTimeout(
      () => this.checkSubmissions(timeout),
      timeout
    );
  }

  async checkSubmissions(prevTime: number) {
    if (!this.hasPendingSubmissions) return;
    const beforeStates = this.subStates;
    await Promise.all(
      this.pendingSubmissions.map(async (sub) => {
        const resp = await cms.getSubmissionShort(
          this.contestName,
          this.taskName,
          sub.uuid
        );
        for (let i = 0; i < this.task.submissions.length; i++) {
          const x = this.task.submissions[i];
          if (x.uuid === sub.uuid) {
            this.task.submissions.splice(i, 1, resp);
            if (resp.result.status === "scored") {
              this.$emit("submission-scored", resp);
            }
          }
        }
      })
    );
    const afterStates = this.subStates;
    const isSame =
      beforeStates.length === afterStates.length &&
      beforeStates.every((x, i) => {
        return x === afterStates[i];
      });
    this.scheduleCheckSubmissions(isSame ? prevTime * 1.2 : 1000);
  }

  @Watch("task.submissions")
  submissionsChanged() {
    this.scheduleCheckSubmissions(1000);
  }

  showCodePanel() {
    this.$router.push({
      name: "CMSTask",
      params: {
        contestName: this.contestName,
        taskName: this.taskName,
      },
    });
  }
}
</script>

<style scoped lang="scss">
@import "~bulma/sass/utilities/mixins";
.date-td {
  width: 0.1%;
  white-space: nowrap;
}
.sub-loading {
  display: inline-block;
  position: relative;
  padding-left: 8px;
  width: 1.5em;
  height: 1em;
}
.sub-loading::after {
  position: absolute !important;
  bottom: 0;
  -webkit-animation: spinAround 0.5s infinite linear;
  animation: spinAround 0.5s infinite linear;
  border: 2px solid #dbdbdb;
  border-radius: 9999px;
  border-right-color: transparent;
  border-top-color: transparent;
  content: "";
  display: block;
  height: 1em;
  width: 1em;
}
tr.is-active {
  background-color: #fcedee;
  color: #df2f38;
}

.wrapper {
  display: flex;
  flex-direction: column;
}

@include touch {
  /* move submissions table to bottom when in touch layout */
  .submissions-block {
    order: 10;
  }
}

.submission-list-move,
.submission-list-enter-active,
.submission-list-leave-active {
  transition: all 0.5s ease;
}

.submission-list-enter-from,
.submission-list-leave-to {
  opacity: 0;
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.submission-list-leave-active {
  position: absolute;
}
</style>

<style scoped lang="scss">
@import "~katex/dist/katex.min.css";
</style>
