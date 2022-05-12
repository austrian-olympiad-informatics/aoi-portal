<template>
  <div v-if="editor" class="editor-container">
    <div class="editor-controls">
      <div
        :class="{
          dropdown: true,
          'editor-control': true,
          active: editor.isActive('heading'),
          'is-active': headingDropDownActive,
        }"
      >
        <div
          class="dropdown-trigger"
          @click="headingDropDownActive = !headingDropDownActive"
        >
          <b-icon icon="format-size" />
        </div>
        <div class="dropdown-menu" id="dropdown-menu" role="menu">
          <div class="dropdown-content">
            <div
              :class="{
                'dropdown-item': true,
                'is-active': editor.isActive('paragraph'),
              }"
              @click="
                editor.chain().focus().setParagraph().run();
                headingDropDownActive = false;
              "
            >
              Paragraph
            </div>
            <div
              :class="{
                'dropdown-item': true,
                'is-size-3': true,
                'is-active': editor.isActive('heading', { level: 1 }),
              }"
              @click="
                editor.chain().focus().toggleHeading({ level: 1 }).run();
                headingDropDownActive = false;
              "
            >
              Heading 1
            </div>
            <div
              :class="{
                'dropdown-item': true,
                'is-size-4': true,
                'is-active': editor.isActive('heading', { level: 2 }),
              }"
              @click="
                editor.chain().focus().toggleHeading({ level: 2 }).run();
                headingDropDownActive = false;
              "
            >
              Heading 2
            </div>
            <div
              :class="{
                'dropdown-item': true,
                'is-size-5': true,
                'is-active': editor.isActive('heading', { level: 3 }),
              }"
              @click="
                editor.chain().focus().toggleHeading({ level: 3 }).run();
                headingDropDownActive = false;
              "
            >
              Heading 3
            </div>
            <div
              :class="{
                'dropdown-item': true,
                'is-size-6': true,
                'is-active': editor.isActive('heading', { level: 4 }),
              }"
              @click="
                editor.chain().focus().toggleHeading({ level: 4 }).run();
                headingDropDownActive = false;
              "
            >
              Heading 4
            </div>
            <div
              :class="{
                'dropdown-item': true,
                'is-size-7': true,
                'is-active': editor.isActive('heading', { level: 5 }),
              }"
              @click="
                editor.chain().focus().toggleHeading({ level: 5 }).run();
                headingDropDownActive = false;
              "
            >
              Heading 5
            </div>
          </div>
        </div>
      </div>
      <div
        @click="editor.chain().focus().toggleBold().run()"
        :class="{ 'editor-control': true, active: editor.isActive('bold') }"
      >
        <b-icon icon="format-bold" />
      </div>
      <div
        @click="editor.chain().focus().toggleUnderline().run()"
        :class="{
          'editor-control': true,
          active: editor.isActive('underline'),
        }"
      >
        <b-icon icon="format-underline" />
      </div>
      <div
        @click="editor.chain().focus().toggleItalic().run()"
        :class="{ 'editor-control': true, active: editor.isActive('italic') }"
      >
        <b-icon icon="format-italic" />
      </div>
      <div
        @click="editor.chain().focus().toggleStrike().run()"
        :class="{ 'editor-control': true, active: editor.isActive('strike') }"
      >
        <b-icon icon="format-strikethrough" />
      </div>
      <div
        @click="onLink"
        :class="{ 'editor-control': true, active: editor.isActive('link') }"
      >
        <b-icon icon="link-variant" />
      </div>
      <div
        @click="editor.chain().focus().toggleCode().run()"
        :class="{ 'editor-control': true, active: editor.isActive('code') }"
      >
        <b-icon icon="code-braces" />
      </div>
      <div
        @click="editor.chain().focus().toggleCodeBlock().run()"
        :class="{
          'editor-control': true,
          active: editor.isActive('codeBlock'),
        }"
      >
        <b-icon icon="code-tags" />
      </div>
      <div
        @click="editor.chain().focus().toggleBulletList().run()"
        :class="{
          'editor-control': true,
          active: editor.isActive('bulletList'),
        }"
      >
        <b-icon icon="format-list-bulleted" />
      </div>
      <div
        @click="editor.chain().focus().toggleOrderedList().run()"
        :class="{
          'editor-control': true,
          active: editor.isActive('orderedList'),
        }"
      >
        <b-icon icon="format-list-numbered" />
      </div>
      <div
        @click="editor.chain().focus().toggleBlockquote().run()"
        :class="{
          'editor-control': true,
          active: editor.isActive('blockquote'),
        }"
      >
        <b-icon icon="format-quote-close" />
      </div>
      <div
        @click="editor.chain().focus().setHorizontalRule().run()"
        :class="{ 'editor-control': true }"
      >
        <b-icon icon="minus" />
      </div>
      <div
        @click="editor.chain().focus().undo().run()"
        :class="{ 'editor-control': true }"
      >
        <b-icon icon="undo" />
      </div>
      <div
        @click="editor.chain().focus().redo().run()"
        :class="{ 'editor-control': true }"
      >
        <b-icon icon="redo" />
      </div>
    </div>
    <bubble-menu :editor="editor" :tippy-options="{ duration: 100 }">
      <div class="bubble-controls">
        <div
          @click="editor.chain().focus().toggleBold().run()"
          :class="{ 'editor-control': true, active: editor.isActive('bold') }"
        >
          <b-icon icon="format-bold" />
        </div>
        <div
          @click="editor.chain().focus().toggleUnderline().run()"
          :class="{
            'editor-control': true,
            active: editor.isActive('underline'),
          }"
        >
          <b-icon icon="format-underline" />
        </div>
        <div
          @click="editor.chain().focus().toggleItalic().run()"
          :class="{ 'editor-control': true, active: editor.isActive('italic') }"
        >
          <b-icon icon="format-italic" />
        </div>
        <div
          @click="editor.chain().focus().toggleStrike().run()"
          :class="{ 'editor-control': true, active: editor.isActive('strike') }"
        >
          <b-icon icon="format-strikethrough" />
        </div>
        <div
          @click="onLink"
          :class="{ 'editor-control': true, active: editor.isActive('link') }"
        >
          <b-icon icon="link-variant" />
        </div>
        <div
          @click="editor.chain().focus().toggleCode().run()"
          :class="{ 'editor-control': true, active: editor.isActive('code') }"
        >
          <b-icon icon="code-braces" />
        </div>
      </div>
    </bubble-menu>
    <editor-content :editor="editor" class="editor" />
  </div>
</template>

<script lang="ts">
import { Editor, EditorContent, BubbleMenu } from "@tiptap/vue-2";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";

@Component({
  components: {
    EditorContent,
    BubbleMenu,
  },
})
export default class RichTextEditor extends Vue {
  editor: Editor | null = null;
  @Prop({
    type: String,
    default: "",
  })
  value!: string;

  headingDropDownActive = false;

  @Watch("value")
  watchValue(value: string) {
    const isSame = this.editor?.getHTML() === value;
    if (!isSame) {
      this.editor?.commands.setContent(value, false);
    }
  }

  mounted() {
    this.editor = new Editor({
      content: this.value,
      extensions: [StarterKit, Underline, Link],
      onUpdate: () => {
        this.$emit("input", this.editor?.getHTML());
      },
      editorProps: {
        attributes: {
          class: "content",
        },
      },
    });
  }

  onLink() {
    if (this.editor?.isActive("link")) {
      this.editor?.chain().focus().unsetLink().run();
      return;
    }
    this.$buefy.dialog.prompt({
      message: `Apply Link`,
      inputAttrs: {
        placeholder: "e.g. https://informatikolympiade.at/AOI/",
      },
      trapFocus: true,
      onConfirm: (value) => {
        this.editor
          ?.chain()
          .focus()
          .toggleLink({
            href: value,
            target: "_blank",
          })
          .run();
      },
    });
  }

  beforeDestroy() {
    this.editor?.destroy();
  }
}
</script>

<style>
.ProseMirror {
  flex-grow: 1;
  outline: 0;
}
</style>

<style lang="scss" scoped>
.editor-container {
  border: 1px solid #acacac;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  width: 100%;
}
.editor {
  flex-grow: 1;
  display: flex;
  background-color: #fff;
  color: #000;
  padding: 30px 20px;
}
.editor-controls {
  padding: 0.5rem;
  border-bottom: 1px solid #acacac;
  display: flex;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.editor-control {
  border: 1px solid transparent;
  box-sizing: border-box;
  align-items: center;
  border-radius: 50%;
  color: #303133;
  cursor: pointer;
  display: flex;
  justify-content: center;
  height: 40px;
  margin: 2px;
  outline: 0;
  transition: all 0.2s ease-in-out;
  width: 40px;

  &:hover {
    background-color: #e4e9f2;
  }

  &.active {
    background-color: #ecf5ff;
    color: #409eff;
  }
}

.dropdown-item {
  &:hover {
    background-color: #e4e9f2;
  }
  &.is-active {
    background-color: #ecf5ff;
    color: #409eff;
  }
}
.dropdown-trigger {
  line-height: 1;
}

.bubble-controls {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 3px 5px -1px #0003, 0 6px 10px #00000024, 0 1px 18px #0000001f;
  display: flex;
  padding: 5px;
  z-index: 50;
}
</style>
