<template>
  <div>
    <div class="sub-head">
      <span class="icon-text">
        <router-link
          :to="{
            name: 'CMSTask',
            params: {
              contestName: contestName,
              taskName: taskName,
            },
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
                <b-table :data="st.testcases" class="subt-table">
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

        <div class="block" v-if="submission.result.testcases">
          <b-table :data="submission.result.testcases" class="subt-table">
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
          <img :src="memeUrl" @load="memeUrlLoaded" loading="lazy" class="meme-img" />
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
              {{ submission.result.compilation_time }} s
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
          </ul>
          <h4 class="title is-6 mb-2 mt-3">Standardausgabe (stdout)</h4>
          <pre>{{ submission.result.compilation_stdout }}</pre>
          <h4 class="title is-6 mb-2 mt-3">Standardfehlerausgabe (stderr)</h4>
          <pre>{{ submission.result.compilation_stderr }}</pre>
        </div>
      </div>

      <div class="is-relative" v-if="files !== null">
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
    </div>
    <div class="sub-loader" v-else>
      <b-loading :is-full-page="false" :active="true" />
    </div>
  </div>
</template>

<script lang="ts">
import { Submission, Task } from "@/types/cms";
import { PropType } from "vue";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import cms from "@/services/cms";
import { formatDateShort } from "@/util/dt";
import { langToExt, lookupCMSLang } from "@/util/lang-table";
import CodeMirror from "@/components/CodeMirror.vue";
import { downloadBlob } from "@/util/download";
import { translateText } from "@/util/cms";

@Component({
  components: {
    CodeMirror,
  },
})
export default class SubmissionDetailsPanel extends Vue {
  @Prop({
    type: Object as PropType<Task>,
  })
  task!: Task;
  now: Date = new Date();
  get contestName(): string {
    return this.$route.params.contestName;
  }
  get taskName(): string {
    return this.$route.params.taskName;
  }
  get submissionUuid(): string {
    return this.$route.params.submissionUuid;
  }
  submission: Submission | null = null;
  files: Record<string, string> | null = null;
  memeUrl: string | null = null;

  async loadSubmission() {
    this.submission = await cms.getSubmission(
      this.contestName,
      this.taskName,
      this.submissionUuid
    );
    if (this.submission.result.meme_digest !== null) {
      const blob = await cms.getSubmissionMeme(
        this.contestName,
        this.taskName,
        this.submissionUuid,
        this.submission.result.meme_digest
      );
      this.memeUrl = URL.createObjectURL(blob);
    }
  }
  memeUrlLoaded() {
    if (this.memeUrl !== null)
      URL.revokeObjectURL(this.memeUrl);
  }
  async loadFiles() {
    this.files = Object.fromEntries(
      await Promise.all(
        this.submission!.files.map(async (file) => {
          const resp = await cms.getSubmissionFile(
            this.contestName,
            this.taskName,
            this.submissionUuid,
            file.filename, file.digest
          );
          return [file.filename, await resp.text()];
        })
      )
    );
  }

  async mounted() {
    this.now = new Date();
    await this.loadSubmission();
    this.scheduleCheckSubmissions(1000);
    await this.loadFiles();
  }

  formatSubDate(date: Date) {
    return formatDateShort(this.now, date);
  }
  translateText(text: string[]) {
    return translateText(text);
  }

  subtaskPoints(st: { max_score: number; score_fraction: number }): number {
    return parseFloat(
      (st.max_score * st.score_fraction).toFixed(this.task.score_precision)
    );
  }

  get codeLang() {
    return lookupCMSLang(this.submission?.language || "");
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

  onKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      this.$router.push({
        name: "CMSTask",
        params: {
          contestName: this.contestName,
          taskName: this.taskName,
        },
      });
    }
  }
  created() {
    document.addEventListener("keydown", this.onKeydown);
  }
  destroyed() {
    document.removeEventListener("keydown", this.onKeydown);
  }
}
</script>

<style scoped>
.wrapper {
  flex-basis: 0;
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
}
.sub-loader {
  height: 100%;
  position: relative;
}
.score-loader {
  height: 200px;
  position: relative;
}
.sub-details {
  flex-basis: 0;
  flex-grow: 1;
  overflow-y: auto;
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
  min-width: 500px;
  max-height: 500px;
  max-width: 500px;
  object-fit: contain;
  margin-left: auto;
  margin-right: auto;
  display: block;
}
</style>
