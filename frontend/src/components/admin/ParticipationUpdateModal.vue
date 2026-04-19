<template>
  <div class="modal-card" style="width: 480px">
    <header class="modal-card-head">
      <p class="modal-card-title">Update Participant</p>
      <button type="button" class="delete" @click="$emit('close')" />
    </header>
    <section class="modal-card-body">
      <form @submit.prevent="updateParticipation(data)" v-if="data !== null">
        <ParticipationForm v-model="data" :user-editable="false" />
        <b-button type="is-primary" native-type="submit">Update</b-button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import admin from "@/services/admin";
import { AdminContestParticipation } from "@/types/admin";
import ParticipationForm, {
  ParticipationFormData,
} from "./ParticipationForm.vue";

const props = defineProps<{
  contestUuid: string;
  participationId: number;
}>();

const emit = defineEmits<{
  submit: [ParticipationFormData];
  close: [];
}>();

const part = ref<AdminContestParticipation | null>(null);
const data = ref<ParticipationFormData | null>(null);

onMounted(async () => {
  part.value = await admin.getContestParticipation(
    props.contestUuid,
    props.participationId,
  );
  data.value = {
    user_id: part.value.user.id,
    cms_id: part.value.cms_id,
    manual_password: part.value.manual_password,
  };
});

function updateParticipation(formData: ParticipationFormData) {
  emit("submit", formData);
  emit("close");
}
</script>
