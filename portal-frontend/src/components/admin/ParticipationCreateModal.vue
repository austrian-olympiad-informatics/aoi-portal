<template>
  <div class="modal-card" style="width: auto">
    <header class="modal-card-head">
      <p class="modal-card-title">Add Participant</p>
      <button type="button" class="delete" @click="$emit('close')" />
    </header>
    <section class="modal-card-body">
      <form @submit.prevent="createParticipation(data)" v-if="data !== null">
        <ParticipationForm v-model="data" :user-editable="true" />
        <b-button type="is-primary" native-type="submit">Create</b-button>
      </form>
    </section>
  </div>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { Component, Prop, Vue } from "vue-property-decorator";
import ParticipationForm, {
  ParticipationFormData,
} from "./ParticipationForm.vue";

@Component({
  components: {
    ParticipationForm,
  },
})
export default class ParticipationCreateModal extends Vue {
  @Prop()
  contestUuid!: string;

  data: ParticipationFormData = {
    user_id: null,
    cms_id: null,
    manual_password: null,
  };

  async createParticipation(data: ParticipationFormData) {
    await admin.createContestParticipation(this.contestUuid, {
      user_id: data.user_id!,
      cms_id: data.cms_id ? +data.cms_id : null,
      manual_password: data.manual_password ? data.manual_password : null,
    });
    this.$buefy.toast.open({
      message: "Participant has been added!",
      type: "is-success",
    });
    this.$emit("close");
  }
}
</script>
