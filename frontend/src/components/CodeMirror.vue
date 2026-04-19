<template>
  <div
    :class="{
      codemirror: true,
      'cm-fullheight': fullheight,
    }"
    ref="codemirror"
  ></div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { onMounted } from "vue";
import {
  Decoration,
  DecorationSet,
  EditorView,
  keymap,
} from "@codemirror/view";
import {
  EditorState,
  Extension,
  StateEffect,
  StateField,
} from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import {
  syntaxHighlighting,
  defaultHighlightStyle,
  indentUnit,
} from "@codemirror/language";
import { javascript } from "@codemirror/lang-javascript";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { python } from "@codemirror/lang-python";
import { rust } from "@codemirror/lang-rust";
import { oneDark, oneDarkHighlightStyle } from "@codemirror/theme-one-dark";
import {
  lineNumbers,
  highlightActiveLineGutter,
  highlightSpecialChars,
  drawSelection,
  dropCursor,
  rectangularSelection,
  crosshairCursor,
  highlightActiveLine,
} from "@codemirror/view";
import {
  foldGutter,
  indentOnInput,
  bracketMatching,
  foldKeymap,
} from "@codemirror/language";
import { history, defaultKeymap, historyKeymap } from "@codemirror/commands";
import { highlightSelectionMatches, searchKeymap } from "@codemirror/search";
import {
  closeBrackets,
  autocompletion,
  closeBracketsKeymap,
  completionKeymap,
} from "@codemirror/autocomplete";
import { lintKeymap } from "@codemirror/lint";
import { StreamLanguage } from "@codemirror/language";
import { go } from "@codemirror/legacy-modes/mode/go";
import { haskell } from "@codemirror/legacy-modes/mode/haskell";
import { c, csharp, kotlin } from "@codemirror/legacy-modes/mode/clike";
import { Language } from "@/util/lang-table";

const addItalic = StateEffect.define<{ from: number; to: number }>();

const italicField = StateField.define<DecorationSet>({
  create() {
    return Decoration.none;
  },
  update(underlines, tr) {
    underlines = underlines.map(tr.changes);
    for (const e of tr.effects)
      if (e.is(addItalic)) {
        underlines = underlines.update({
          add: [italicMark.range(e.value.from, e.value.to)],
        });
      }
    return underlines;
  },
  provide: (f) => EditorView.decorations.from(f),
});

const italicMark = Decoration.mark({ class: "cm-italic" });

const italicTheme = EditorView.baseTheme({
  ".cm-italic": { fontStyle: "italic" },
});

const fontTheme = EditorView.theme({
  ".cm-scroller": {
    fontFamily: "'Fira Code', monospace",
  },
});

function italicAll(view: EditorView) {
  if (view.state.doc.length === 0) return;
  const effects: StateEffect<unknown>[] = [
    addItalic.of({ from: 0, to: view.state.doc.length }),
  ];
  if (!view.state.field(italicField, false))
    effects.push(StateEffect.appendConfig.of([italicField, italicTheme]));
  view.dispatch({ effects });
}

const props = withDefaults(
  defineProps<{
    modelValue?: string;
    lang?: Language;
    darkTheme?: boolean;
    fullheight?: boolean;
    editable?: boolean;
    readonly?: boolean;
    italic?: boolean;
  }>(),
  {
    modelValue: "",
    lang: Language.None,
    darkTheme: true,
    fullheight: true,
    editable: true,
    readonly: false,
    italic: false,
  },
);

const emit = defineEmits<{ "update:modelValue": [string] }>();

const codemirror = ref<HTMLElement | null>(null);
let doc: string | null = null;
let view: EditorView;

const extensions = computed<Extension[]>(() =>
  [
    lineNumbers(),
    highlightActiveLineGutter(),
    highlightSpecialChars(),
    history(),
    foldGutter(),
    drawSelection(),
    dropCursor(),
    EditorState.allowMultipleSelections.of(true),
    indentOnInput(),
    syntaxHighlighting(
      props.darkTheme ? oneDarkHighlightStyle : defaultHighlightStyle,
      { fallback: true },
    ),
    props.darkTheme ? oneDark : undefined,
    fontTheme,
    bracketMatching(),
    closeBrackets(),
    autocompletion(),
    rectangularSelection(),
    crosshairCursor(),
    highlightActiveLine(),
    highlightSelectionMatches(),
    props.readonly ? EditorState.readOnly.of(props.readonly) : undefined,
    props.editable ? EditorView.editable.of(props.editable) : undefined,
    props.lang === Language.Python ? EditorState.tabSize.of(4) : undefined,
    props.lang === Language.Python ? indentUnit.of("    ") : undefined,
    keymap.of([
      ...closeBracketsKeymap,
      ...defaultKeymap,
      ...searchKeymap,
      ...historyKeymap,
      ...foldKeymap,
      ...completionKeymap,
      ...lintKeymap,
    ]),
    keymap.of([indentWithTab]),
    props.lang === Language.CSharp ? StreamLanguage.define(csharp) : undefined,
    props.lang === Language.C ? StreamLanguage.define(c) : undefined,
    props.lang === Language.Cpp ? cpp() : undefined,
    props.lang === Language.Go ? StreamLanguage.define(go) : undefined,
    props.lang === Language.Haskell
      ? StreamLanguage.define(haskell)
      : undefined,
    props.lang === Language.Haskell
      ? StreamLanguage.define(haskell)
      : undefined,
    props.lang === Language.Java ? java() : undefined,
    props.lang === Language.Javascript ? javascript() : undefined,
    props.lang === Language.Kotlin ? StreamLanguage.define(kotlin) : undefined,
    props.lang === Language.Python ? python() : undefined,
    props.lang === Language.Rust ? rust() : undefined,
    props.lang === Language.Typescript
      ? javascript({ typescript: true })
      : undefined,
  ].filter((x): x is Extension => x !== undefined),
);

function makeUpdateListener() {
  return EditorView.updateListener.of((update) => {
    if (!update.docChanged) return;
    doc = update.state.doc.toString();
    emit("update:modelValue", doc);
  });
}

function resetState() {
  view.setState(
    EditorState.create({
      doc: doc || "",
      extensions: [...extensions.value, makeUpdateListener()],
      selection: view.state.selection,
    }),
  );
  if (props.italic) {
    italicAll(view);
  }
}

onMounted(() => {
  doc = props.modelValue;
  view = new EditorView({
    state: EditorState.create({
      doc: doc,
      extensions: [...extensions.value, makeUpdateListener()],
    }),
    parent: codemirror.value as Element,
  });
  if (props.italic) {
    italicAll(view);
  }
});

watch(() => props.italic, resetState);
watch(() => props.lang, resetState);
watch(() => props.modelValue, (value) => {
  if (value === doc) return;
  doc = value;
  view.dispatch({
    changes: {
      from: 0,
      to: view.state.doc.length,
      insert: doc,
    },
  });
});
</script>

<style>
.codemirror.cm-fullheight {
  height: 100%;
  max-height: 100%;
}
.cm-fullheight .cm-editor {
  height: 100%;
}
.cm-fullheight .cm-scroller {
  flex-basis: 0;
  flex-grow: 1;
  overflow: auto;
}
</style>
