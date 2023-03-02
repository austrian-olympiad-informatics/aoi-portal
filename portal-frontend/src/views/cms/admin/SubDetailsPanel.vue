<template>
  <div>
    <div class="sub-head">
      <span class="icon-text">
        <router-link
          :to="{
            name: 'CMSAdminSubmissions',
            query: $route.query,
          }"
        >
          <b-icon class="sub-head-back has-text-white" icon="arrow-left" />
        </router-link>
        <span>
          Einsendung&nbsp;
          <span v-if="submission !== null">
            {{ formatSubDate(new Date(submission.timestamp)) }}
          </span>
        </span>
      </span>
    </div>
    <div class="sub-details" v-if="submission !== null">
      <div class="sub-details-inner">
        <div class="block">
          <table>
            <tbody>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="calendar" />
                    <span><b>Timestamp</b></span>
                  </span>
                </td>
                <td>{{ formatSubDate(new Date(submission.timestamp)) }}</td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="account" />
                    <span><b>User</b></span>
                  </span>
                </td>
                <td>
                  <router-link
                    :to="{
                      name: 'CMSAdminUser',
                      params: { userId: submission.participation.user.id },
                    }"
                  >
                    {{ formatUser(submission.participation.user) }}
                  </router-link>
                </td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="medal" />
                    <span><b>Contest</b></span>
                  </span>
                </td>
                <td>
                  <router-link
                    :to="{
                      name: 'CMSAdminContest',
                      params: { contestId: submission.contest.id },
                    }"
                  >
                    {{ submission.contest.description }}
                  </router-link>
                </td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="briefcase" />
                    <span><b>Task</b></span>
                  </span>
                </td>
                <td>
                  <router-link
                    :to="{
                      name: 'CMSAdminTask',
                      params: { taskId: submission.task.id },
                    }"
                  >
                    {{ `${submission.task.name} - ${submission.task.title}` }}
                  </router-link>
                </td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="certificate" />
                    <span><b>Official</b></span>
                  </span>
                </td>
                <td>{{ submission.official ? "Yes" : "No" }}</td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="web" />
                    <span><b>Language</b></span>
                  </span>
                </td>
                <td>{{ submission.language }}</td>
              </tr>
              <tr v-if="submission.comment">
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="pencil" />
                    <span><b>Comment</b></span>
                  </span>
                </td>
                <td>{{ submission.comment }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="block" v-if="submission.result.subtasks">
          <div
            class="mb-3"
            v-for="(st, index) in submission.result.subtasks"
            :key="index"
          >
            <b-collapse class="panel" animation="none" :open="false">
              <template #trigger="props">
                <div class="panel-heading" role="button">
                  <b-icon
                    :icon="props.open ? 'chevron-down' : 'chevron-right'"
                  />
                  <strong> Teilaufgabe {{ index + 1 }} </strong>
                  <span
                    :class="{
                      'st-head-result': true,
                      tag: true,
                      'is-success': subtaskPoints(st) >= st.max_score,
                      'is-danger': subtaskPoints(st) <= 0,
                      'is-warning':
                        subtaskPoints(st) > 0 &&
                        subtaskPoints(st) < st.max_score,
                      'is-pulled-right': true,
                      'is-medium': true,
                    }"
                  >
                    {{ subtaskPoints(st) }} / {{ st.max_score }}
                  </span>
                </div>
              </template>

              <div class="panel-block">
                <b-table
                  :data="st.testcases"
                  class="subt-table"
                  :mobile-cards="false"
                >
                  <b-table-column label="#" numeric v-slot="props">
                    {{ props.index + 1 }}
                  </b-table-column>
                  <b-table-column label="Ergebnis" v-slot="props">
                    <span
                      class="tag is-success"
                      v-if="props.row.outcome === 'Correct'"
                    >
                      Korrekt
                    </span>
                    <span
                      class="tag is-danger"
                      v-else-if="props.row.outcome === 'Not correct'"
                    >
                      Nicht korrekt
                    </span>
                    <span class="tag is-warning" v-else>
                      Teilweise korrekt
                    </span>
                  </b-table-column>
                  <b-table-column label="Details" v-slot="props">
                    {{ translateText(props.row.text) }}
                  </b-table-column>
                  <b-table-column label="Ausführungszeit" v-slot="props">
                    {{ props.row.time.toFixed(3) }} s
                  </b-table-column>
                  <b-table-column label="Speichernutzung" v-slot="props">
                    {{ (props.row.memory / (1024 * 1024)).toFixed(2) }} MiB
                  </b-table-column>
                </b-table>
              </div>
            </b-collapse>
          </div>
        </div>

        <div class="is-relative block codepanel" v-if="files !== null">
          <div class="is-relative" v-for="(value, fname) in files" :key="fname">
            <b-button
              type="is-link is-light"
              icon-right="download"
              class="download-button"
              @click="downloadFile(fname, value)"
            />
            <CodeMirror
              :value="value"
              :lang="codeLang"
              :fullheight="false"
              :editable="false"
              :readonly="true"
            />
          </div>
        </div>

        <div class="block" v-if="submission.result.testcases">
          <b-table
            :data="submission.result.testcases"
            class="subt-table"
            :mobile-cards="false"
          >
            <b-table-column label="#" numeric v-slot="props">
              {{ props.index + 1 }}
            </b-table-column>
            <b-table-column label="Ergebnis" v-slot="props">
              <span
                class="tag is-success"
                v-if="props.row.outcome === 'Correct'"
              >
                Korrekt
              </span>
              <span
                class="tag is-danger"
                v-else-if="props.row.outcome === 'Not correct'"
              >
                Nicht korrekt
              </span>
              <span class="tag is-warning" v-else> Teilweise korrekt </span>
            </b-table-column>
            <b-table-column label="Details" v-slot="props">
              {{ translateText(props.row.text) }}
            </b-table-column>
            <b-table-column label="Ausführungszeit" v-slot="props">
              {{ props.row.time.toFixed(3) }} s
            </b-table-column>
            <b-table-column label="Speichernutzung" v-slot="props">
              {{ (props.row.memory / (1024 * 1024)).toFixed(2) }} MiB
            </b-table-column>
          </b-table>
        </div>

        <div
          class="block score-loader"
          v-if="
            ['compiling', 'evaluating', 'scoring'].includes(
              submission.result.status
            )
          "
        >
          <b-loading :is-full-page="false" :active="true" />
        </div>

        <div class="block" v-if="memeUrl !== null">
          <img
            :src="memeUrl"
            @load="memeUrlLoaded"
            loading="lazy"
            class="meme-img"
          />
        </div>

        <div class="block" v-if="scores !== null">
          <h3 class="title is-4 mb-2">Current User Score</h3>
          <div class="pr-1 pl-1">
            <PointsBar
              :score="scoreTaskScore.score"
              :max-score="scoreTaskInfo.max_score"
              :score-precision="scoreTaskInfo.score_precision"
              :show-max-score="true"
              :subtasks="scoreSubtasks"
            />
          </div>
        </div>

        <div class="block" v-if="submission.result.compilation_text">
          <h3 class="title is-4">Kompilierungsausgabe</h3>
          <ul>
            <li>
              <strong>Kompilierungsergebnis:</strong>
              {{ submission.result.compilation_text }}
            </li>
            <li>
              <strong>Kompilierungszeit:</strong>
              {{ submission.result.compilation_time }} s ({{
                submission.result.compilation_wall_clock_time
              }}
              s)
            </li>
            <li>
              <strong>Speichernutzung:</strong>
              {{
                (submission.result.compilation_memory / (1024 * 1024)).toFixed(
                  1
                )
              }}
              MiB
            </li>
            <li>
              <strong>Compilation sandbox:</strong>&nbsp;
              <code>{{ submission.result.compilation_sandbox }}</code>
              (shard #{{ submission.result.compilation_shard }})
            </li>
            <li>
              <strong>Executables:</strong>&nbsp;
              <code
                class="is-clickable"
                @click="downloadExecutable(exe)"
                v-for="exe in submission.result.executables"
                :key="exe.id"
                >{{ exe.filename }}</code
              >
            </li>
          </ul>
          <h4 class="title is-6 mb-2 mt-3">Standardausgabe (stdout)</h4>
          <pre>{{ submission.result.compilation_stdout }}</pre>
          <h4 class="title is-6 mb-2 mt-3">Standardfehlerausgabe (stderr)</h4>
          <pre>{{ submission.result.compilation_stderr }}</pre>
        </div>
      </div>

      <div
        class="block pt-3 pb-3 pr-3 pl-3"
        v-if="submission.result.evaluations"
      >
        <h2 class="title is-4">Evaluations</h2>
        <b-table
          :data="submission.result.evaluations"
          narrowed
          scrollable
          :mobile-cards="false"
        >
          <b-table-column label="Testcase" v-slot="props">
            {{ props.row.testcase.codename }}
          </b-table-column>
          <b-table-column label="Ergebnis" v-slot="props">
            <span class="tag is-success" v-if="props.row.outcome >= 1">
              Korrekt
            </span>
            <span class="tag is-danger" v-else-if="props.row.outcome <= 0">
              Nicht korrekt
            </span>
            <span class="tag is-warning" v-else>
              Teilweise korrekt ({{ props.row.outcome }})</span
            >
          </b-table-column>
          <b-table-column label="Text" v-slot="props">
            {{ props.row.text[0] }}
          </b-table-column>
          <b-table-column label="Time" v-slot="props">
            {{ props.row.execution_time.toFixed(3) }} s ({{
              props.row.execution_wall_clock_time.toFixed(3)
            }}
            s)
          </b-table-column>
          <b-table-column label="Memory" v-slot="props">
            {{ (props.row.execution_memory / 1024 / 1024).toFixed(2) }} MiB
          </b-table-column>
          <b-table-column label="Sandbox" v-slot="props">
            <code>{{ props.row.evaluation_sandbox }}</code>
            (#{{ props.row.evaluation_shard }})
          </b-table-column>
        </b-table>
      </div>
    </div>
    <div class="sub-loader" v-else>
      <b-loading :is-full-page="false" :active="true" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { formatDateShort } from "@/util/dt";
import { langToExt, lookupCMSLang } from "@/util/lang-table";
import CodeMirror from "@/components/CodeMirror.vue";
import { downloadBlob } from "@/util/download";
import { translateText } from "@/util/cms";
import cmsadmin from "@/services/cmsadmin";
import {
  AdminExecutable,
  AdminSubmissionDetailed,
  AdminSubmissionResultScoredShort,
  AdminUserShort,
  AdminParticipationScore,
} from "@/types/cmsadmin";
import PointsBar from "../PointsBar.vue";

@Component({
  components: {
    CodeMirror,
    PointsBar,
  },
})
export default class AdminSubmissionDetailsPanel extends Vue {
  now: Date = new Date();
  get submissionUuid(): string {
    return this.$route.params.submissionUuid;
  }
  submission: AdminSubmissionDetailed | null = null;
  files: Record<string, string> | null = null;
  memeUrl: string | null = null;
  scores: AdminParticipationScore | null = null;

  async loadMeme() {
    if (this.submission!.result.meme_digest === null) return;
    const blob = await cmsadmin.getDigest(this.submission!.result.meme_digest);
    this.memeUrl = URL.createObjectURL(blob);
  }

  async loadSubmission() {
    this.submission = await cmsadmin.getSubmission(this.submissionUuid);
    await Promise.all([this.loadMeme(), this.loadFiles(), this.loadScores()]);
  }
  async loadScores() {
    this.scores = await cmsadmin.getParticipationScore(
      this.submission!.participation.id
    );
  }
  get scoreTaskScore() {
    return this.scores?.task_scores.find(
      (task) => task.id === this.submission!.task.id
    );
  }
  get scoreTaskInfo() {
    return this.scores?.tasks.find(
      (task) => task.id === this.submission!.task.id
    );
  }
  get scoreSubtasks() {
    return this.scoreTaskInfo?.subtask_max_scores?.map((x, i) => {
      return {
        max_score: x,
        score: this.scoreTaskScore?.subtask_scores?.[i] || 0.0,
      };
    });
  }
  memeUrlLoaded() {
    if (this.memeUrl !== null) URL.revokeObjectURL(this.memeUrl);
  }
  async loadFiles() {
    if (this.files !== null) return;
    this.files = Object.fromEntries(
      await Promise.all(
        this.submission!.files.map(async (file) => {
          const resp = await cmsadmin.getDigest(file.digest);
          return [file.filename, await resp.text()];
        })
      )
    );
  }

  async mounted() {
    this.now = new Date();
    await this.loadSubmission();
    this.scheduleCheckSubmissions(1000);
  }

  formatSubDate(date: Date) {
    return formatDateShort(this.now, date);
  }
  translateText(text: string[]) {
    return translateText(text);
  }
  formatUser(user: AdminUserShort) {
    return `${user.first_name} ${user.last_name} (${user.username})`;
  }

  async downloadExecutable(exe: AdminExecutable) {
    const blob = await cmsadmin.getDigest(exe.digest);
    downloadBlob(blob, exe.filename);
  }

  subtaskPoints(st: { max_score: number; fraction: number }): number {
    const res = this.submission?.result as AdminSubmissionResultScoredShort;
    return parseFloat(
      (st.max_score * st.fraction).toFixed(res.score_precision)
    );
  }

  get codeLang() {
    return lookupCMSLang(this.submission?.language || "");
  }

  checkSubTimeout: number | null = null;

  scheduleCheckSubmissions(timeout: number) {
    if (this.checkSubTimeout !== null) clearTimeout(this.checkSubTimeout);
    this.checkSubTimeout = window.setTimeout(
      () => this.checkSubmissions(timeout),
      timeout
    );
  }

  async checkSubmissions(prevTime: number) {
    if (
      ["compilation_failed", "scored"].includes(
        this.submission!.result.status || ""
      )
    )
      return;
    const prevState = this.submission!.result.status;
    await this.loadSubmission();
    const newState = this.submission!.result.status;
    this.scheduleCheckSubmissions(
      prevState === newState ? prevTime * 1.2 : 1000
    );
  }

  @Watch("task.submissions")
  submissionsChanged() {
    this.scheduleCheckSubmissions(1000);
  }

  downloadFile(fname: string, value: string) {
    const blob = new Blob([value]);
    const lang = lookupCMSLang(this.submission!.language);
    fname = fname.replaceAll(".%l", langToExt(lang));
    downloadBlob(blob, fname);
  }
}
</script>

<style scoped lang="scss">
@import "~bulma/sass/utilities/mixins";

.sub-loader {
  height: 100%;
  position: relative;
}
.score-loader {
  height: 200px;
  position: relative;
}
.sub-head {
  background-color: #606060;
  color: #ffffff;
  font-size: 1.25em;
  font-weight: 700;
  line-height: 1.25;
  padding: 0.75em 1em;
  width: 100%;
}
.sub-head-back {
  margin-right: 0.5em !important;
}
.sub-details-inner {
  padding: 15px;
}
.subt-table {
  width: 100%;
}
.st-head-result {
  margin-top: -0.2rem;
}
.download-button {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
}
.meme-img {
  width: 500px;
  max-height: 500px;
  object-fit: contain;
  margin-left: auto;
  margin-right: auto;
  display: block;
}
@include mobile {
  .meme-img {
    width: 300px;
  }
}
.codepanel {
  margin-left: -15px;
  margin-right: -15px;
}
</style>
