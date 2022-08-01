<template>
  <div class="container">
    <section class="section" v-if="task !== null">
      <b-breadcrumb align="is-left" size="is-left">
        <b-breadcrumb-item tag="router-link" :to="{ name: 'CMSAdminIndex' }">
          Admin Panel
        </b-breadcrumb-item>
        <b-breadcrumb-item
          tag="router-link"
          :to="{
            name: 'CMSAdminContest',
            params: { contestId: task.contest.id },
          }"
          v-if="task.contest !== null"
        >
          {{ task.contest.description }}
        </b-breadcrumb-item>
        <b-breadcrumb-item
          tag="router-link"
          :to="{ name: 'CMSAdminTask', params: { taskId } }"
          active
        >
          {{ task.name }}
        </b-breadcrumb-item>
      </b-breadcrumb>
      <h1 class="title is-2">
        Admin - Task {{ task.name }} - {{ task.title }}
      </h1>
      <div class="block">
        <ul>
          <li>ID: {{ task.id }}</li>
          <li>Name: {{ task.name }}</li>
          <li>Title: {{ task.title }}</li>
          <li v-if="task.contest !== null">
            Contest:
            <router-link
              :to="{
                name: 'CMSAdminContest',
                params: { contestId: task.contest.id },
              }"
            >
              {{ task.contest.description }}
            </router-link>
          </li>
          <li v-else>Contest: Not Assigned</li>
          <li>Score mode: {{ task.score_mode }}</li>
          <li>Score precision: {{ task.score_precision }}</li>
          <li>
            Submission format:
            <span v-for="(f, i) in task.submission_format" :key="f">
              <code>{{ f }}</code>
              <span v-if="i + 1 < task.submission_format.length">, </span>
            </span>
          </li>
          <li>
            Memory Limit:
            {{ (dataset.memory_limit / 1024 / 1024).toFixed(1) }} MiB
          </li>
          <li>Time Limit: {{ dataset.time_limit == null ? 'None' : dataset.time_limit.toFixed(1) }} s</li>
        </ul>
      </div>
      <div class="block content">
        <h2 class="title is-4">Files</h2>
        <ul>
          <li v-if="task.statements.length">
            Statements:
            <ul>
              <li v-for="stat in task.statements" :key="stat.id">
                <a @click="downloadStatement(stat)">{{
                  stat.language.toUpperCase()
                }}</a>
              </li>
            </ul>
          </li>
          <li v-else>No statements</li>
          <li v-if="task.attachments.length">
            Attachments:
            <ul>
              <li v-for="att in task.attachments" :key="att.id">
                <a @click="downloadAttachment(att)"
                  ><code>{{ att.filename }}</code></a
                >
              </li>
            </ul>
          </li>
          <li v-else>No attachments</li>
          <li v-if="dataset.managers.length">
            Managers:
            <ul>
              <li v-for="man in dataset.managers" :key="man.id">
                <a @click="downloadManager(man)"
                  ><code>{{ man.filename }}</code></a
                >
              </li>
            </ul>
          </li>
          <li v-else>No managers</li>
          <li v-if="dataset.test_managers.length">
            Test managers:
            <ul>
              <li v-for="man in dataset.test_managers" :key="man.id">
                <a @click="downloadTestManager(man)"
                  ><code>{{ man.filename }}</code></a
                >
              </li>
            </ul>
          </li>
          <li v-else>No test managers</li>
          <li v-if="dataset.language_templates.length">
            Language templates:
            <ul>
              <li v-for="lt in dataset.language_templates" :key="lt.id">
                <a @click="downloadLanguageTemplate(lt)"
                  ><code>{{ lt.filename }}</code></a
                >
              </li>
            </ul>
          </li>
          <li v-else>No language templates</li>
        </ul>
      </div>
      <div class="block">
        <h2 class="title is-4">Extra</h2>
        <p>Task Type: {{ dataset.task_type }}</p>
        <p>
          Task Type Parameters:
          <code>{{ JSON.stringify(dataset.task_type_parameters) }}</code>
        </p>
        <p>Score Type: {{ dataset.score_type }}</p>
        <p>
          Score Type Parameters:
          <code>{{ JSON.stringify(dataset.score_type_parameters) }}</code>
        </p>
      </div>
      <div class="block" v-if="submissions !== null">
        <h2 class="title is-4">Submissions</h2>
        <router-link
          :to="{ name: 'CMSAdminSubmissions', query: { task_id: taskId } }"
        >
          {{ submissions.total }} submissions
        </router-link>
      </div>
      <div class="block">
        <h2 class="title is-4">Testcases</h2>
        <b-table
          :data="dataset.testcases"
          custom-row-key="id"
          narrowed
          detailed
          detail-key="id"
          custom-detail-row
          @details-open="testcaseOpen"
          class="testcase-table"
        >
          <b-table-column label="Testcase" v-slot="props">
            {{ props.row.codename }}
          </b-table-column>
          <b-table-column label="Public" v-slot="props">
            {{ props.row.public }}
          </b-table-column>

          <template #detail="props">
            <tr class="detail">
              <td colspan="3" class="testcase-td">
                <div class="testcase-wrapper" :key="`tc${props.row.id}-${testcaseKey}`">
                  <div class="testcase testcase-input">
                    <b-button
                      type="is-link is-light"
                      icon-right="download"
                      class="download-button"
                      @click="downloadTestcaseInput(props.row)"
                    />
                    <CodeMirror
                      :editable="false"
                      :readonly="true"
                      :value="testcaseDigests.get(props.row.input_digest) || ''"
                    />
                  </div>
                  <div class="testcase testcase-output">
                    <b-button
                      type="is-link is-light"
                      icon-right="download"
                      class="download-button"
                      @click="downloadTestcaseInput(props.row)"
                    />
                    <CodeMirror
                      :editable="false"
                      :readonly="true"
                      :value="testcaseDigests.get(props.row.output_digest) || ''"
                    />
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </b-table>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import cmsadmin from "@/services/cmsadmin";
import {
  AdminAttachment,
  AdminLanguageTemplate,
  AdminManager,
  AdminStatement,
  AdminSubmissionsPaginated,
  AdminTaskDetailed,
  AdminTestcase,
  AdminTestManager,
} from "@/types/cmsadmin";
import { downloadBlob } from "@/util/download";
import { formatDateShort } from "@/util/dt";
import { Component, Vue } from "vue-property-decorator";
import CodeMirror from "@/components/CodeMirror.vue";

@Component({
  components: {
    CodeMirror,
  },
})
export default class AdminTaskView extends Vue {
  get taskId(): number {
    return +this.$route.params.taskId;
  }
  task: AdminTaskDetailed | null = null;
  submissions: AdminSubmissionsPaginated | null = null;

  get dataset() {
    return this.task === null ? null : this.task.active_dataset;
  }

  async loadTask() {
    this.task = await cmsadmin.getTask(this.taskId);
  }
  async loadSubmissions() {
    this.submissions = await cmsadmin.getSubmissions({
      taskId: this.taskId,
      perPage: 0,
    });
  }
  async mounted() {
    await Promise.all([this.loadTask(), this.loadSubmissions()]);
  }
  formatDate(date: string) {
    return formatDateShort(new Date(), new Date(date));
  }

  async downloadStatement(stat: AdminStatement) {
    const blob = await cmsadmin.getDigest(stat.digest);
    downloadBlob(
      blob,
      `${this.task!.name} (${stat.language.toUpperCase()}).pdf`
    );
  }
  async downloadAttachment(att: AdminAttachment) {
    const blob = await cmsadmin.getDigest(att.digest);
    downloadBlob(blob, att.filename);
  }
  async downloadManager(man: AdminManager) {
    const blob = await cmsadmin.getDigest(man.digest);
    downloadBlob(blob, man.filename);
  }
  async downloadTestManager(man: AdminTestManager) {
    const blob = await cmsadmin.getDigest(man.digest);
    downloadBlob(blob, man.filename);
  }
  async downloadLanguageTemplate(lt: AdminLanguageTemplate) {
    const blob = await cmsadmin.getDigest(lt.digest);
    downloadBlob(blob, lt.filename);
  }

  testcaseDigests: Map<string, string> = new Map();
  testcaseKey = 0;

  async testcaseOpen(tc: AdminTestcase) {
    await Promise.all(
      [tc.input_digest, tc.output_digest].map(async (digest) => {
        const blob = await cmsadmin.getDigest(digest);
        this.testcaseDigests.set(digest, await blob.text());
      })
    );
    this.testcaseKey += 1;
  }
  downloadTestcaseInput(tc: AdminTestcase) {
    const blob = new Blob([this.testcaseDigests.get(tc.input_digest)!]);
    downloadBlob(blob, `${tc.codename}.txt`);
  }
  downloadTestcaseOutput(tc: AdminTestcase) {
    const blob = new Blob([this.testcaseDigests.get(tc.output_digest)!]);
    downloadBlob(blob, `${tc.codename}.txt`);
  }
}
</script>

<style scoped>
.testcase-table {
  width: 100%;
}
.testcase-td {
  padding: 0 !important;
  position: relative;
  height: 500px;
}
.testcase-wrapper {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  flex-direction: row;
}
.testcase {
  display: flex;
  flex-direction: column;
  flex-grow: 0;
  flex: none;
  width: 50%;
  position: relative;
}
.testcase-input {
  border-right: 2px solid #17191e;
}
.download-button {
  position: absolute;
  bottom: 16px;
  right: 16px;
  z-index: 10;
}
</style>
