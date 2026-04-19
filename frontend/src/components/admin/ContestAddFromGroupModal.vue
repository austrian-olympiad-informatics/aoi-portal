<template>
  <form @submit.prevent="submit">
    <div class="modal-card" style="width: 480px">
      <header class="modal-card-head">
        <p class="modal-card-title">Add From Group</p>
        <button type="button" class="delete" @click="$emit('close')" />
      </header>
      <section class="modal-card-body">
        <b-field>
          <b-select
            placeholder="Select a group"
            required
            v-model="selected"
            expanded
          >
            <option v-for="group in groups" :value="group.id" :key="group.id">
              {{ group.name }}
            </option>
          </b-select>
        </b-field>
        <b-field>
          <b-checkbox v-model="randomPasswords"
            >Initialize users with random passwords</b-checkbox
          >
        </b-field>
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
import { AdminGroups } from "@/types/admin";

const emit = defineEmits<{
  submit: [{ selected: number | null; randomPasswords: boolean }];
  close: [];
}>();

const groups = ref<AdminGroups | null>(null);
const selected = ref<number | null>(null);
const randomPasswords = ref(false);

onMounted(async () => {
  groups.value = await admin.getGroups();
});

function submit() {
  emit("submit", {
    selected: selected.value,
    randomPasswords: randomPasswords.value,
  });
  emit("close");
}
</script>
