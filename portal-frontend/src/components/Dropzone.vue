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


<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Dropzone extends Vue {
  dropzoneActive: boolean = false;

  dropzoneDragenter(e: DragEvent) {
    this.dropzoneActive = true;
    if (e.dataTransfer !== null) e.dataTransfer.dropEffect = "copy";
    e.preventDefault();
  }
  dropzoneDragover(e: DragEvent) {
    this.dropzoneActive = true;
    if (e.dataTransfer !== null) e.dataTransfer.dropEffect = "copy";
    e.preventDefault();
  }
  dropzoneDragleave() {
    this.dropzoneActive = false;
  }
  dropzoneDrop(e: DragEvent) {
    this.dropzoneActive = false;
    if (e.dataTransfer === null) return;
    this.$emit("drop", e.dataTransfer.files);
  }
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
