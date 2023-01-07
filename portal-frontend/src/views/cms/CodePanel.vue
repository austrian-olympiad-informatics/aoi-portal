<template>
  <div class="wrapper">
    <div
      :class="{
        'code-wrap': true,
        'code-wrap-test': isTestMode,
      }"
    >
      <div class="code-main">
        <Dropzone @drop="onMainDrop">
          <CodeMirror
            v-model="code"
            @input="codeChanged"
            :lang="codemirrorLang"
          />
        </Dropzone>
      </div>
      <div class="code-test" v-if="isTestMode">
        <div class="code-test-input">
          <div class="test-head">Test Input</div>
          <Dropzone @drop="onInputDrop">
            <CodeMirror v-model="testInput" @input="testInputChanged" />
          </Dropzone>
        </div>
        <div class="code-test-output">
          <div class="test-head">Test Output</div>
          <div class="code-test-output-wrap">
            <CodeMirror
              :value="testOutput"
              :editable="false"
              :readonly="true"
              :italic="testOutputItalic"
            />
            <div class="loading-overlay is-active" v-if="testEvalLoading">
              <div class="loading-background"></div>
              <div class="loading-icon"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="code-bar">
      <b-field class="code-bar-test">
        <b-switch
          v-model="isTestMode"
          outlined
          type="is-primary"
          passive-type="is-light"
        >
          <span class="code-bar-test-text">Test Modus</span>
        </b-switch>
      </b-field>
      <div class="code-bar-lang">
        <div class="select">
          <select v-model="lang" @change="newLangSelected">
            <option v-for="lang of task.languages" :key="lang" :value="lang">
              {{ lang }}
            </option>
          </select>
        </div>
      </div>
      <div class="code-bar-submit">
        <b-button type="is-primary" @click="submitCode" v-if="!isTestMode" :loading="submitLoading">
          Abschicken
        </b-button>
        <b-button type="is-primary" @click="testCode" v-if="isTestMode" :loading="submitLoading">
          Testen
        </b-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { SubmitResult, Task, UserEval, UserEvalSubmitResult } from "@/types/cms";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { PropType } from "vue";
import CodeMirror from "@/components/CodeMirror.vue";
import Dropzone from "@/components/Dropzone.vue";
import cms from "@/services/cms";
import { b64DecodeUnicode, b64EncodeUnicode } from "@/util/base64";
import { extToLang, langToCMSLang, lookupCMSLang } from "@/util/lang-table";
import { translateText } from "@/util/cms";
import { matchError } from "@/util/errors";

interface CodeStorage {
  language: string;
  code: string;
  isTestMode: boolean;
  testInput: string;
}

@Component({
  components: {
    CodeMirror,
    Dropzone,
  },
})
export default class CodePanel extends Vue {
  @Prop({
    type: Object as PropType<Task>,
  })
  task!: Task;
  get contestName(): string {
    return this.$route.params.contestName;
  }
  get taskName(): string {
    return this.$route.params.taskName;
  }

  code = "";
  lang = "";
  testInput = "";
  testEvalUuid: string | null = null;
  testEvalTimeoutHandle: number | null = null;
  testEval: UserEval | null = null;
  testEvalLoading = false;
  submitLoading = false;
  get testOutput(): string | null {
    if (this.testEval === null) return "Noch nicht ausgeführt";
    if (this.testEval.result.status === "compilation_failed")
      return this.testEval.result.compilation_stderr + '\n' + this.testEval.result.compilation_stdout;
    if (this.testEval.result.status !== "evaluated")
      return "Wird ausgeführt...";
    const translatedEvalText = translateText(this.testEval.result.evaluation_text);
    if (this.testEval.result.output === undefined)
      return translatedEvalText;
    const decodedOutput = b64DecodeUnicode(this.testEval.result.output);
    if (this.testEval.result.evaluation_text[0] === "Execution completed successfully")
      return decodedOutput;
    return `(${translatedEvalText})\n\n${decodedOutput}`;
  }
  get testOutputItalic(): boolean {
    if (this.testEval === null) return true;
    if (this.testEval.result.status === "compilation_failed") return false;
    if (this.testEval.result.status !== "evaluated") return true;
    if (this.testEval.result.output === undefined) return true;
    return false;
  }
  isTestMode = false;

  get languageTemplatesByCMSLang(): Map<string, { filename: string; digest: string; }> {
    return new Map(this.task.language_templates.map((x) => {
      const ext = x.filename.substr(x.filename.lastIndexOf("."));
      return [langToCMSLang(extToLang(ext), this.task.languages), x];
    }));
  }

  async setDefaults() {
    if (!this.lang.length || !this.task.languages.includes(this.lang)) {
      const order = [
        "C++20 / g++",
        "C++17 / g++",
        "C++11 / g++",
        "Python 3 / CPython",
        ...this.task.languages,
      ];
      for (const l of order) {
        if (this.task.languages.includes(l)) {
          this.lang = l;
          break;
        }
      }
    }
    if (!this.code.length) {
      const lt = this.languageTemplatesByCMSLang.get(this.lang);
      if (lt !== undefined) {
        const resp = await cms.getLanguageTemplate(
          this.contestName,
          this.taskName,
          lt.filename,
          lt.digest
        );
        this.code = await resp.text();
        this.codeChanged();
      }
    }
  }

  get storageKey() {
    return `cms$${this.contestName}$${this.taskName}`;
  }
  saveStorageData() {
    const data: CodeStorage = {
      language: this.lang,
      code: this.code,
      isTestMode: this.isTestMode,
      testInput: this.testInput,
    };
    window.localStorage.setItem(this.storageKey, JSON.stringify(data));
  }
  restoreStorageData() {
    const s = window.localStorage.getItem(this.storageKey);
    if (s === null) return;
    const data: CodeStorage = JSON.parse(s);
    this.lang = data.language;
    this.code = data.code;
    this.isTestMode = data.isTestMode;
    this.testInput = data.testInput;
  }
  codeChanged() {
    this.saveStorageData();
  }
  @Watch("lang")
  langChanged() {
    this.saveStorageData();
  }
  @Watch("isTestMode")
  testModeChanged() {
    this.saveStorageData();
    this.loadDefaultInput();
  }
  async loadDefaultInput() {
    if (this.testInput !== "" || this.task.default_input_digest === null) return;
    const resp = await cms.getDefaultInput(this.contestName, this.taskName, this.task.default_input_digest);
    this.testInput = await resp.text();
  }
  get codemirrorLang() {
    return lookupCMSLang(this.lang);
  }

  async submitCode() {
    this.submitLoading = true;
    let resp: SubmitResult;
    try {
      resp = await cms.submit(this.contestName!, this.taskName!, {
        language: this.lang,
        files: [
          {
            filename: this.task!.submission_format[0],
            content: b64EncodeUnicode(this.code),
          },
        ],
      });
    } catch (err) {
      matchError(err, {
        throttled: "Einsendungen zu schnell hintereinander!",
        default:
          "Beim Abschicken ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    } finally {
      this.submitLoading = false;
    }
    this.$emit("new-submission", resp.submission);
  }

  async mounted() {
    this.restoreStorageData();
    await this.setDefaults();
    await this.loadDefaultInput();
  }

  async onMainDrop(files: FileList) {
    for (const file of files) {
      const fname = file.name;
      const ext = fname.substr(fname.lastIndexOf("."));
      const lang = extToLang(ext);
      this.lang = langToCMSLang(lang, this.task.languages);
      this.code = await file.text();
      this.codeChanged();
    }
  }
  async onInputDrop(files: FileList) {
    for (const file of files) {
      this.testInput = await file.text();
      this.testInputChanged();
    }
  }

  newLangSelected() {
    const lt = this.languageTemplatesByCMSLang.get(this.lang);
    if (lt === undefined) return;
    this.$buefy.dialog.confirm({
      message: "Möchtest du die Vorlage für diese Sprache laden?",
      onConfirm: async () => {
        const resp = await cms.getLanguageTemplate(
          this.contestName,
          this.taskName,
          lt.filename,
          lt.digest
        );
        this.code = await resp.text();
        this.codeChanged();
      },
    });
  }

  testInputChanged() {
    this.saveStorageData();
  }

  async testCode() {
    if (this.testEvalTimeoutHandle !== null)
      clearTimeout(this.testEvalTimeoutHandle);

    
    this.submitLoading = true;
    let resp: UserEvalSubmitResult;
    try {
      resp = await cms.userEval(this.contestName!, this.taskName!, {
        language: this.lang,
        files: [
          {
            filename: this.task!.submission_format[0],
            content: b64EncodeUnicode(this.code),
          },
        ],
        input: b64EncodeUnicode(this.testInput),
      });
    } catch (err) {
      matchError(err, {
        throttled: "Einsendungen zu schnell hintereinander!",
        default:
          "Beim Abschicken ist etwas schiefgelaufen. Bitte versuche es später erneut.",
      });
      return;
    } finally {
      this.submitLoading = false;
    }
    this.testEval = null;
    this.testEvalUuid = resp.uuid;
    this.testEvalLoading = true;

    const reschedule = (time: number) => {
      this.testEvalTimeoutHandle = setTimeout(async () => {
        const resp = await cms.getUserEval(
          this.contestName,
          this.taskName,
          this.testEvalUuid!
        );
        const oldStatus = this.testEval?.result.status || "";
        this.testEval = resp;
        if (["compilation_failed", "evaluated"].includes(resp.result.status)) {
          this.testEvalLoading = false;
          return;
        }
        const newStatus = this.testEval.result.status;
        const newTime = newStatus !== oldStatus ? 1000 : time * 1.2;
        reschedule(newTime);
      }, time);
    };
    reschedule(1000);
  }
}
</script>

<style scoped lang="scss">
@import "~bulma/sass/utilities/mixins";

@include touch {
  .wrapper {
    min-height: 100vh;
  }
}

.code-wrap {
  flex-basis: 0;
  flex-grow: 1;
  height: 100%;
}
.code-wrap-test {
  display: flex;
  flex-direction: column;
}

.code-main {
  height: 100%;
}
.code-wrap-test .code-main {
  flex-basis: 50%;
}
.code-wrap-test .code-test {
  flex-basis: 50%;
  display: flex;
  flex-direction: row;
}
.code-test-input {
  border-right: 1px solid #17191e;
}
.code-test-input,
.code-test-output {
  display: flex;
  flex-direction: column;
  flex: none;
  width: 50%;
}
.test-head {
  background-color: #17191e;
  color: #ededed;
  padding: 0.75em 1em;
  padding-top: 1.25em;
  width: 100%;
}
.code-test-output-wrap {
  position: relative;
  height: 100%;
}
.loading-background {
  background: rgba(255, 255, 255, 0.15) !important;
}

@include touch {
  .code-test {
    flex-direction: column !important;
  }
  .code-test-input,
  .code-test-output {
    width: 100%;
    min-height: 300px;
  }
  .code-main {
    min-height: 500px;
  }
}

.code-bar {
  padding: 16px;
  background-color: #13181d;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  z-index: 10;
  flex-wrap: wrap;
}
.code-bar-test {
  margin-bottom: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.code-bar-test-text {
  color: white;
}
.code-bar-lang {
  flex: 1;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  margin-bottom: 0;
}
.code-bar-lang select {
  background-color: transparent;
  color: white;
  border: none !important;
  box-shadow: none !important;
}
.code-bar-lang select::after {
  border-color: white;
}
.code-bar-submit {
  flex: 1;
  display: flex;
  flex-direction: row-reverse;
}
</style>
