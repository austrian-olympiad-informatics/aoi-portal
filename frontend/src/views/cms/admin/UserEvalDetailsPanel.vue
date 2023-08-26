<template>
  <div>
    <div class="sub-head">
      <span class="icon-text">
        <router-link
          :to="{
            name: 'CMSAdminUserEvals',
            query: $route.query,
          }"
        >
          <b-icon class="sub-head-back has-text-white" icon="arrow-left" />
        </router-link>
        <span>
          User Eval&nbsp;
          <span v-if="userEval !== null">
            {{ formatSubDate(new Date(userEval.timestamp)) }}
          </span>
        </span>
      </span>
    </div>
    <div class="sub-details" v-if="userEval !== null">
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
                <td>{{ formatSubDate(new Date(userEval.timestamp)) }}</td>
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
                      params: { userId: userEval.participation.user.id },
                    }"
                  >
                    {{ formatUser(userEval.participation.user) }}
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
                      params: { contestId: userEval.contest.id },
                    }"
                  >
                    {{ userEval.contest.description }}
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
                      params: { taskId: userEval.task.id },
                    }"
                  >
                    {{ `${userEval.task.name} - ${userEval.task.title}` }}
                  </router-link>
                </td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="web" />
                    <span><b>Language</b></span>
                  </span>
                </td>
                <td>{{ userEval.language }}</td>
              </tr>
            </tbody>
          </table>
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

        <div class="block" v-if="inputFile !== null">
          <h2 class="title is-5 mb-2">Input</h2>
          <div class="is-relative codepanel">
            <div class="is-relative">
              <b-button
                type="is-link is-light"
                icon-right="download"
                class="download-button"
                @click="downloadFile('input', inputFile)"
              />
              <CodeMirror
                :value="inputFile"
                :fullheight="false"
                :editable="false"
                :readonly="true"
              />
            </div>
          </div>
        </div>

        <div class="block" v-if="userEval.result.status === 'evaluated'">
          <table>
            <tbody>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="timer-outline" />
                    <span><b>Execution Time</b></span>
                  </span>
                </td>
                <td>{{ userEval.result.execution_time }} s</td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="clock-outline" />
                    <span><b>Execution Wall Clock Time</b></span>
                  </span>
                </td>
                <td>{{ userEval.result.execution_wall_clock_time }} s</td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="memory" />
                    <span><b>Execution Memory</b></span>
                  </span>
                </td>
                <td>
                  {{
                    (userEval.result.execution_memory / (1024 * 1024)).toFixed(
                      2,
                    )
                  }}
                  MiB
                </td>
              </tr>
              <tr>
                <td class="pr-5">
                  <span class="icon-text">
                    <b-icon icon="calendar" />
                    <span><b>Sandbox</b></span>
                  </span>
                </td>
                <td>
                  <code>{{ userEval.result.evaluation_sandbox }}</code> (shard
                  #{{ userEval.result.evaluation_shard }})
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          class="block"
          v-if="userEval.result.status === 'compilation_failed'"
        >
          <b>Compilation failed, no output</b>
        </div>

        <div class="block" v-if="outputFile !== null">
          <h2 class="title is-5 mb-2">Output</h2>
          <div class="is-relative codepanel">
            <div class="is-relative">
              <b-button
                type="is-link is-light"
                icon-right="download"
                class="download-button"
                @click="downloadFile('output', outputFile)"
              />
              <CodeMirror
                :value="outputFile"
                :fullheight="false"
                :editable="false"
                :readonly="true"
              />
            </div>
          </div>
        </div>

        <div
          class="block score-loader"
          v-if="['compiling', 'evaluating'].includes(userEval.result.status)"
        >
          <b-loading :is-full-page="false" :active="true" />
        </div>

        <div class="block" v-if="userEval.result.compilation_text">
          <h3 class="title is-4">Kompilierungsausgabe</h3>
          <ul>
            <li>
              <strong>Kompilierungsergebnis:</strong>
              {{ userEval.result.compilation_text }}
            </li>
            <li>
              <strong>Kompilierungszeit:</strong>
              {{ userEval.result.compilation_time }} s ({{
                userEval.result.compilation_wall_clock_time
              }}
              s)
            </li>
            <li>
              <strong>Speichernutzung:</strong>
              {{
                (userEval.result.compilation_memory / (1024 * 1024)).toFixed(1)
              }}
              MiB
            </li>
            <li>
              <strong>Compilation sandbox:</strong>&nbsp;
              <code>{{ userEval.result.compilation_sandbox }}</code>
              (shard #{{ userEval.result.compilation_shard }})
            </li>
            <li>
              <strong>Executables:</strong>&nbsp;
              <code
                class="is-clickable"
                @click="downloadExecutable(exe)"
                v-for="exe in userEval.result.executables"
                :key="exe.id"
                >{{ exe.filename }}</code
              >
            </li>
          </ul>
          <h4 class="title is-6 mb-2 mt-3">Standardausgabe (stdout)</h4>
          <pre>{{ userEval.result.compilation_stdout }}</pre>
          <h4 class="title is-6 mb-2 mt-3">Standardfehlerausgabe (stderr)</h4>
          <pre>{{ userEval.result.compilation_stderr }}</pre>
        </div>
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
  AdminUserEvalDetailed,
  AdminUserShort,
} from "@/types/cmsadmin";

@Component({
  components: {
    CodeMirror,
  },
})
export default class AdminUserEvalDetailsPanel extends Vue {
  now: Date = new Date();
  get userEvalUuid(): string {
    return this.$route.params.userEvalUuid;
  }
  userEval: AdminUserEvalDetailed | null = null;
  files: Record<string, string> | null = null;
  inputFile: string | null = null;
  outputFile: string | null = null;

  async loadUserEval() {
    this.userEval = await cmsadmin.getUserEval(this.userEvalUuid);
    await Promise.all([this.loadFiles(), this.loadInput(), this.loadOutput()]);
  }
  async loadFiles() {
    if (this.files !== null) return;
    this.files = Object.fromEntries(
      await Promise.all(
        this.userEval!.files.map(async (file) => {
          const resp = await cmsadmin.getDigest(file.digest);
          return [file.filename, await resp.text()];
        }),
      ),
    );
  }
  async loadInput() {
    if (this.inputFile !== null) return;
    const resp = await cmsadmin.getDigest(this.userEval!.input_digest);
    this.inputFile = await resp.text();
  }
  async loadOutput() {
    if (this.outputFile !== null) return;
    const res = this.userEval!.result;
    if (res.status === "evaluated") {
      const resp = await cmsadmin.getDigest(res.output_digest);
      this.outputFile = await resp.text();
    }
  }

  async mounted() {
    this.now = new Date();
    await this.loadUserEval();
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

  get codeLang() {
    return lookupCMSLang(this.userEval?.language || "");
  }

  checkSubTimeout: number | null = null;

  scheduleCheckSubmissions(timeout: number) {
    if (this.checkSubTimeout !== null) clearTimeout(this.checkSubTimeout);
    this.checkSubTimeout = window.setTimeout(
      () => this.checkSubmissions(timeout),
      timeout,
    );
  }

  async checkSubmissions(prevTime: number) {
    if (
      ["compilation_failed", "evaluated"].includes(
        this.userEval!.result.status || "",
      )
    )
      return;
    const prevState = this.userEval!.result.status;
    await this.loadUserEval();
    const newState = this.userEval!.result.status;
    this.scheduleCheckSubmissions(
      prevState === newState ? prevTime * 1.2 : 1000,
    );
  }

  @Watch("task.submissions")
  submissionsChanged() {
    this.scheduleCheckSubmissions(1000);
  }

  downloadFile(fname: string, value: string) {
    const blob = new Blob([value]);
    const lang = lookupCMSLang(this.userEval!.language);
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
