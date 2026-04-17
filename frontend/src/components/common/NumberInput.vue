<template>
  <b-input
    :value="valueStr"
    @input="setValue(e.target.value)"
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
  readonly value!: number | null;

  valueStr: string | null = null;

  setValue(val: string) {
    this.valueStr = val;
    this.$emit("input", val ? +val : null);
  }

  @Watch("value")
  onValueChanged(val: number | null) {
    this.valueStr = val === null ? "" : val.toString();
  }

  mounted() {
    this.valueStr = this.value === null ? "" : this.value.toString();
  }
}
export default toNative(NumberInput)
</script>
