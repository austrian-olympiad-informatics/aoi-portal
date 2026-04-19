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
              :model-value="testOutput"
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
        <b-button
          type="is-primary"
          @click="submitCode"
          v-if="!isTestMode"
          :loading="submitLoading"
        >
          Abschicken
        </b-button>
        <b-button
          type="is-primary"
          @click="testCode"
          v-if="isTestMode"
          :loading="submitLoading"
        >
          Testen
        </b-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  SubmitResult,
  Task,
  UserEval,
  UserEvalSubmitResult,
} from "@/types/cms";
import { ref, computed, watch, onMounted } from "vue";
import { PropType } from "vue";
import { useRoute } from "vue-router";
import { useDialog } from "buefy";
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

const props = defineProps<{ task: Task }>();
const emit = defineEmits<{ "new-submission": [unknown] }>();

const route = useRoute();
const dialog = useDialog();

const contestName = computed(() => route.params.contestName as string);
const taskName = computed(() => route.params.taskName as string);

const code = ref("");
const lang = ref("");
const testInput = ref("");
const testEvalUuid = ref<string | null>(null);
const testEvalTimeoutHandle = ref<number | null>(null);
const testEval = ref<UserEval | null>(null);
const testEvalLoading = ref(false);
const submitLoading = ref(false);
const isTestMode = ref(false);

const testOutput = computed<string | null>(() => {
  if (testEval.value === null) return "Noch nicht ausgeführt";
  if (testEval.value.result.status === "compilation_failed")
    return (
      testEval.value.result.compilation_stderr +
      "\n" +
      testEval.value.result.compilation_stdout
    );
  if (testEval.value.result.status !== "evaluated") return "Wird ausgeführt...";
  const translatedEvalText = translateText(
    testEval.value.result.evaluation_text,
  );
  if (testEval.value.result.output === undefined) return translatedEvalText;
  const decodedOutput = b64DecodeUnicode(testEval.value.result.output);
  if (
    testEval.value.result.evaluation_text[0] ===
    "Execution completed successfully"
  )
    return decodedOutput;
  return `(${translatedEvalText})\n\n${decodedOutput}`;
});

const testOutputItalic = computed<boolean>(() => {
  if (testEval.value === null) return true;
  if (testEval.value.result.status === "compilation_failed") return false;
  if (testEval.value.result.status !== "evaluated") return true;
  if (testEval.value.result.output === undefined) return true;
  return false;
});

const languageTemplatesByCMSLang = computed(
  () =>
    new Map(
      props.task.language_templates.map((x) => {
        const ext = x.filename.substr(x.filename.lastIndexOf("."));
        return [langToCMSLang(extToLang(ext), props.task.languages), x];
      }),
    ),
);

const codemirrorLang = computed(() => lookupCMSLang(lang.value));

const storageKey = computed(
  () => `cms$${contestName.value}$${taskName.value}`,
);

function saveStorageData() {
  const data: CodeStorage = {
    language: lang.value,
    code: code.value,
    isTestMode: isTestMode.value,
    testInput: testInput.value,
  };
  window.localStorage.setItem(storageKey.value, JSON.stringify(data));
}

function restoreStorageData() {
  const s = window.localStorage.getItem(storageKey.value);
  if (s === null) return;
  const data: CodeStorage = JSON.parse(s);
  lang.value = data.language;
  code.value = data.code;
  isTestMode.value = data.isTestMode;
  testInput.value = data.testInput;
}

function codeChanged() {
  saveStorageData();
}

watch(lang, () => {
  saveStorageData();
});

watch(isTestMode, () => {
  saveStorageData();
  loadDefaultInput();
});

async function loadDefaultInput() {
  if (testInput.value !== "" || props.task.default_input_digest === null)
    return;
  const resp = await cms.getDefaultInput(
    contestName.value,
    taskName.value,
    props.task.default_input_digest,
  );
  testInput.value = await resp.text();
}

async function setDefaults() {
  if (!lang.value.length || !props.task.languages.includes(lang.value)) {
    const order = [
      "C++20 / g++",
      "C++17 / g++",
      "C++11 / g++",
      "Python 3 / CPython",
      ...props.task.languages,
    ];
    for (const l of order) {
      if (props.task.languages.includes(l)) {
        lang.value = l;
        break;
      }
    }
  }
  if (!code.value.length) {
    const lt = languageTemplatesByCMSLang.value.get(lang.value);
    if (lt !== undefined) {
      const resp = await cms.getLanguageTemplate(
        contestName.value,
        taskName.value,
        lt.filename,
        lt.digest,
      );
      code.value = await resp.text();
      codeChanged();
    }
  }
}

async function submitCode() {
  submitLoading.value = true;
  let resp: SubmitResult;
  try {
    resp = await cms.submit(contestName.value!, taskName.value!, {
      language: lang.value,
      files: [
        {
          filename: props.task!.submission_format[0],
          content: b64EncodeUnicode(code.value),
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
    submitLoading.value = false;
  }
  emit("new-submission", resp.submission);
}

onMounted(async () => {
  restoreStorageData();
  await setDefaults();
  await loadDefaultInput();
});

async function onMainDrop(files: FileList) {
  for (const file of files) {
    const fname = file.name;
    const ext = fname.substr(fname.lastIndexOf("."));
    const fileLang = extToLang(ext);
    lang.value = langToCMSLang(fileLang, props.task.languages);
    code.value = await file.text();
    codeChanged();
  }
}

async function onInputDrop(files: FileList) {
  for (const file of files) {
    testInput.value = await file.text();
    testInputChanged();
  }
}

function newLangSelected() {
  const lt = languageTemplatesByCMSLang.value.get(lang.value);
  if (lt === undefined) return;
  dialog.confirm({
    message: "Möchtest du die Vorlage für diese Sprache laden?",
    onConfirm: async () => {
      const resp = await cms.getLanguageTemplate(
        contestName.value,
        taskName.value,
        lt.filename,
        lt.digest,
      );
      code.value = await resp.text();
      codeChanged();
    },
  });
}

function testInputChanged() {
  saveStorageData();
}

async function testCode() {
  if (testEvalTimeoutHandle.value !== null)
    clearTimeout(testEvalTimeoutHandle.value);

  submitLoading.value = true;
  let resp: UserEvalSubmitResult;
  try {
    resp = await cms.userEval(contestName.value!, taskName.value!, {
      language: lang.value,
      files: [
        {
          filename: props.task!.submission_format[0],
          content: b64EncodeUnicode(code.value),
        },
      ],
      input: b64EncodeUnicode(testInput.value),
    });
  } catch (err) {
    matchError(err, {
      throttled: "Einsendungen zu schnell hintereinander!",
      default:
        "Beim Abschicken ist etwas schiefgelaufen. Bitte versuche es später erneut.",
    });
    return;
  } finally {
    submitLoading.value = false;
  }
  testEval.value = null;
  testEvalUuid.value = resp.uuid;
  testEvalLoading.value = true;

  const reschedule = (time: number) => {
    testEvalTimeoutHandle.value = window.setTimeout(async () => {
      const resp = await cms.getUserEval(
        contestName.value,
        taskName.value,
        testEvalUuid.value!,
      );
      const oldStatus = testEval.value?.result.status || "";
      testEval.value = resp;
      if (["compilation_failed", "evaluated"].includes(resp.result.status)) {
        testEvalLoading.value = false;
        return;
      }
      const newStatus = testEval.value.result.status;
      const newTime = newStatus !== oldStatus ? 1000 : time * 1.2;
      reschedule(newTime);
    }, time);
  };
  reschedule(1000);
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
