<template>
  <b-autocomplete
    :data="filteredData"
    :loading="loading"
    v-model="bValue"
    :custom-formatter="formatter"
    :required="required"
    open-on-focus
    @select="bSelect"
    clearable
  >
  </b-autocomplete>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator";

@Component
export default class SimpleAutoselect extends Vue {
  @Prop({
    type: Array,
    default: () => [],
  })
  readonly data!: any[] | null;
  
  @Prop()
  readonly value!: any;

  @Prop({
    type: Boolean,
    default: false,
  })
  readonly loading!: boolean;

  @Prop({
    type: Boolean,
    default: false,
  })
  readonly required!: boolean;

  @Prop({
    default: (x: any) => x,
  })
  readonly valueFunc!: (val: any) => any;

  @Prop({
    default: (x: any) => x,
  })
  readonly formatter!: (val: any) => string;

  bValue = "";

  bSelect(newValue: any) {
    this.$emit('input', newValue === null ? null : this.valueFunc(newValue));
  }

  resetBValueFromValue() {
    if (this.value === null) {
      this.bValue = "";
      return;
    }
    if (this.filteredData === null)
      return;
    for (const val of this.filteredData) {
      if (this.valueFunc(val) === this.value) {
        this.bValue = this.formatter(val);
      }
    }
  }

  mounted() {
    this.resetBValueFromValue();
  }

  @Watch("value")
  onValueChanged() {
    this.resetBValueFromValue();
  }

  @Watch("data")
  onDataChanged() {
    this.resetBValueFromValue();
  }

  get filteredData() {
    if (this.data === null)
      return null;
    return this.data
      .filter((x) => {
        return (
            this.formatter(x).toLowerCase().indexOf(this.bValue.toLowerCase()) >= 0
        );
      });
  }
}
</script>
