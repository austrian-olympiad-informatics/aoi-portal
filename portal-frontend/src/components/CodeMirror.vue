<template>
  <div
    :class="{
      codemirror: true,
      'cm-fullheight': fullheight,
    }"
    ref="codemirror"
  ></div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import {
  Decoration,
  DecorationSet,
  EditorView,
  keymap,
} from "@codemirror/view";
import {
  EditorState,
  Transaction,
  Extension,
  StateEffect,
  StateField,
} from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import {
  syntaxHighlighting,
  defaultHighlightStyle,
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
import { swift } from "@codemirror/legacy-modes/mode/swift";
import { c, csharp, kotlin } from "@codemirror/legacy-modes/mode/clike";
import { Language } from "@/util/lang-table";

const addItalic = StateEffect.define<{ from: number; to: number }>();

const italicField = StateField.define<DecorationSet>({
  create() {
    return Decoration.none;
  },
  update(underlines, tr) {
    underlines = underlines.map(tr.changes);
    for (let e of tr.effects)
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
  addItalic.of;
  let effects: StateEffect<unknown>[] = [
    addItalic.of({ from: 0, to: view.state.doc.length }),
  ];
  if (!view.state.field(italicField, false))
    effects.push(StateEffect.appendConfig.of([italicField, italicTheme]));
  view.dispatch({ effects });
}

@Component
export default class CodeMirror extends Vue {
  @Prop({
    type: String,
    default: "",
  })
  value!: string;
  doc: string | null = null;

  @Prop({
    type: String,
    default: Language.None,
  })
  lang!: Language;

  @Prop({
    type: Boolean,
    default: true,
  })
  darkTheme!: boolean;

  @Prop({
    type: Boolean,
    default: true,
  })
  fullheight!: boolean;
  @Prop({
    type: Boolean,
    default: true,
  })
  editable!: boolean;
  @Prop({
    type: Boolean,
    default: false,
  })
  readonly!: boolean;
  @Prop({
    type: Boolean,
    default: false,
  })
  italic!: boolean;

  view!: EditorView;

  get extensions(): Extension[] {
    return [
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
        this.darkTheme ? oneDarkHighlightStyle : defaultHighlightStyle,
        { fallback: true }
      ),
      this.darkTheme ? oneDark : undefined,
      fontTheme,
      bracketMatching(),
      closeBrackets(),
      autocompletion(),
      rectangularSelection(),
      crosshairCursor(),
      highlightActiveLine(),
      highlightSelectionMatches(),
      this.readonly ? EditorState.readOnly.of(this.readonly) : undefined,
      this.editable ? EditorView.editable.of(this.editable) : undefined,
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
      this.lang === Language.CSharp ? StreamLanguage.define(csharp) : undefined,
      this.lang === Language.C ? StreamLanguage.define(c) : undefined,
      this.lang === Language.Cpp ? cpp() : undefined,
      this.lang === Language.Go ? StreamLanguage.define(go) : undefined,
      this.lang === Language.Haskell
        ? StreamLanguage.define(haskell)
        : undefined,
      this.lang === Language.Haskell
        ? StreamLanguage.define(haskell)
        : undefined,
      this.lang === Language.Java ? java() : undefined,
      this.lang === Language.Javascript ? javascript() : undefined,
      this.lang === Language.Kotlin ? StreamLanguage.define(kotlin) : undefined,
      this.lang === Language.Python ? python() : undefined,
      this.lang === Language.Rust ? rust() : undefined,
      this.lang === Language.Typescript
        ? javascript({ typescript: true })
        : undefined,
    ].filter((x): x is Extension => x !== undefined);
  }

  mounted() {
    this.doc = this.value;
    this.view = new EditorView({
      state: EditorState.create({
        doc: this.doc,
        extensions: this.extensions,
      }),
      parent: this.$refs.codemirror as Element,
      dispatch: (tr: Transaction) => {
        this.view.update([tr]);
        if (tr.changes.empty) return;

        this.doc = this.view.state.doc.toString();
        this.$emit("input", this.doc);
      },
    });
    if (this.italic) {
      italicAll(this.view);
    }
  }

  resetState() {
    this.view.setState(
      EditorState.create({
        doc: this.doc || "",
        extensions: this.extensions,
        selection: this.view.state.selection,
      })
    );
    if (this.italic) {
      italicAll(this.view);
    }
  }

  @Watch("italic")
  watchItalic() {
    this.resetState();
  }

  @Watch("value")
  watchValue(value: string) {
    if (value === this.doc) return;
    this.doc = value;
    this.view.dispatch({
      changes: {
        from: 0,
        to: this.view.state.doc.length,
        insert: this.doc,
      },
    });
  }

  @Watch("lang")
  watchLang() {
    this.resetState();
  }
}
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
