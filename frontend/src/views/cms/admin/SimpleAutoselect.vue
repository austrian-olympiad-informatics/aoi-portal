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

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { onMounted } from "vue";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const props = withDefaults(defineProps<{
  data?: any[] | null;
  modelValue?: any;
  loading?: boolean;
  required?: boolean;
  valueFunc?: (val: any) => any; // eslint-disable-line @typescript-eslint/no-explicit-any
  formatter?: (val: any) => string; // eslint-disable-line @typescript-eslint/no-explicit-any
}>(), {
  data: () => [],
  loading: false,
  required: false,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  valueFunc: (x: any) => x,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formatter: (x: any) => x,
});

const emit = defineEmits<{ "update:modelValue": [any] }>(); // eslint-disable-line @typescript-eslint/no-explicit-any

const bValue = ref("");

const filteredData = computed(() => {
  if (props.data === null) return null;
  return props.data!.filter((x) =>
    props.formatter(x).toLowerCase().indexOf(bValue.value.toLowerCase()) >= 0,
  );
});

function resetBValueFromValue() {
  if (props.modelValue === null) {
    bValue.value = "";
    return;
  }
  if (filteredData.value === null) return;
  for (const val of filteredData.value) {
    if (props.valueFunc(val) === props.modelValue) {
      bValue.value = props.formatter(val);
    }
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function bSelect(newValue: any) {
  emit("update:modelValue", newValue === null ? null : props.valueFunc(newValue));
}

watch(() => props.modelValue, resetBValueFromValue);
watch(() => props.data, resetBValueFromValue);

onMounted(() => {
  resetBValueFromValue();
});
</script>
