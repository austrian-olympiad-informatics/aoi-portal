<template>
  <div class="modal-card" style="width: auto">
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

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import ParticipationForm, {
  ParticipationFormData,
} from "./ParticipationForm.vue";

@Component({
  components: {
    ParticipationForm,
  },
})
export default class ParticipationCreateModal extends Vue {
  data: ParticipationFormData = {
    user_id: null,
    cms_id: null,
    manual_password: null,
  };

  async createParticipation() {
    this.$emit("submit", this.data);
    this.$emit("close");
  }
}
</script>
