<template>
  <b-input
    :model-value="valueStr"
    @update:model-value="setValue"
    inputmode="numeric"
    pattern="[0-9]*"
  />
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";

const props = defineProps<{ modelValue?: number | null }>();
const emit = defineEmits<{ "update:modelValue": [number | null] }>();

const valueStr = ref<string | null>(null);

function setValue(val: string) {
  valueStr.value = val;
  const num = val === "" ? null : Number(val);
  if (num !== null && isNaN(num)) return;
  emit("update:modelValue", num);
}

watch(
  () => props.modelValue,
  (val) => {
    const expected = val == null ? "" : val.toString();
    if (valueStr.value === expected) return;
    valueStr.value = expected;
  },
);

onMounted(() => {
  valueStr.value = props.modelValue == null ? "" : props.modelValue.toString();
});
</script>
