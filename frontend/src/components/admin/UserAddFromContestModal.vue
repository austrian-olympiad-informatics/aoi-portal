<template>
  <form @submit.prevent="submit">
    <div class="modal-card" style="width: 480px">
      <header class="modal-card-head">
        <p class="modal-card-title">Add From Contest</p>
        <button type="button" class="delete" @click="$emit('close')" />
      </header>
      <section class="modal-card-body">
        <b-select placeholder="Select a contest" required v-model="selected">
          <option
            v-for="contest in contests"
            :value="contest.uuid"
            :key="contest.uuid"
          >
            {{ contest.name }}
          </option>
        </b-select>
      </section>
      <footer class="modal-card-foot">
        <b-button label="Cancel" @click="$emit('close')" />
        <b-button label="Submit" type="is-primary" native-type="submit" />
      </footer>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import admin from "@/services/admin";
import { AdminContests } from "@/types/admin";

const emit = defineEmits<{
  submit: [string | null];
  close: [];
}>();

const contests = ref<AdminContests | null>(null);
const selected = ref<string | null>(null);

onMounted(async () => {
  contests.value = await admin.getContests();
});

function submit() {
  emit("submit", selected.value);
  emit("close");
}
</script>
