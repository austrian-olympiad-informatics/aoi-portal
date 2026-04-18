<template>
  <div class="modal-card" style="width: 480px">
    <header class="modal-card-head">
      <p class="modal-card-title">Add Participant</p>
      <button type="button" class="delete" @click="$emit('close')" />
    </header>
    <section class="modal-card-body">
      <form @submit.prevent="createParticipation" v-if="data !== null">
        <ParticipationForm v-model="data" :user-editable="true" />
        <b-button type="is-primary" native-type="submit">Create</b-button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import ParticipationForm, {
  ParticipationFormData,
} from "./ParticipationForm.vue";

const emit = defineEmits<{
  submit: [data: ParticipationFormData];
  close: [];
}>();

const data = ref<ParticipationFormData>({
  user_id: null,
  cms_id: null,
  manual_password: null,
});

async function createParticipation() {
  emit("submit", data.value);
  emit("close");
}
</script>
