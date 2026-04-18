<template>
  <div
    class="dropzone-wrapper"
    @dragenter.prevent="dropzoneDragenter"
    @dragover.prevent="dropzoneDragover"
    @dragleave="dropzoneDragleave"
  >
    <div
      class="dropzone"
      :style="{
        display: dropzoneActive ? 'block' : 'none',
      }"
      @drop.prevent="dropzoneDrop"
    ></div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{ drop: [files: FileList] }>();

const dropzoneActive = ref(false);

function dropzoneDragenter(e: DragEvent) {
  dropzoneActive.value = true;
  if (e.dataTransfer !== null) e.dataTransfer.dropEffect = "copy";
  e.preventDefault();
}
function dropzoneDragover(e: DragEvent) {
  dropzoneActive.value = true;
  if (e.dataTransfer !== null) e.dataTransfer.dropEffect = "copy";
  e.preventDefault();
}
function dropzoneDragleave() {
  dropzoneActive.value = false;
}
function dropzoneDrop(e: DragEvent) {
  dropzoneActive.value = false;
  if (e.dataTransfer === null) return;
  emit("drop", e.dataTransfer.files);
}
</script>

<style scoped>
.dropzone-wrapper {
  position: relative;
  height: 100%;
}
.dropzone {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 100;
  background: rgba(0, 123, 255, 0.329);
  border: 11px dashed #8a151b;
}
</style>
