<template>
  <b-input
    :model-value="valueStr"
    @update:model-value="setValue"
    inputmode="numeric"
    pattern="[0-9]*"
  />
</template>

<script lang="ts">
import {  Vue, Component, Watch, Prop, toNative } from "vue-facing-decorator";

@Component
class NumberInput extends Vue {
  @Prop({
    type: Number,
  })
  readonly modelValue!: number | null;

  valueStr: string | null = null;

  setValue(val: string) {
    this.valueStr = val;
    this.$emit("update:modelValue", val ? +val : null);
  }

  @Watch("modelValue")
  onValueChanged(val: number | null) {
    this.valueStr = val === null ? "" : val.toString();
  }

  mounted() {
    this.valueStr = this.modelValue === null ? "" : this.modelValue.toString();
  }
}
export default toNative(NumberInput)
</script>
