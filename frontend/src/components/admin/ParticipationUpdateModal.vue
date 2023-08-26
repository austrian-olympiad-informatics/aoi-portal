<template>
  <div class="modal-card" style="width: auto">
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

<script lang="ts">
import admin from "@/services/admin";
import { AdminContestParticipation } from "@/types/admin";
import { Component, Prop, Vue } from "vue-property-decorator";
import ParticipationForm, {
  ParticipationFormData,
} from "./ParticipationForm.vue";

@Component({
  components: {
    ParticipationForm,
  },
})
export default class ParticipationUpdateModal extends Vue {
  @Prop()
  contestUuid!: string;
  @Prop()
  participationId!: number;

  part: AdminContestParticipation | null = null;
  data: ParticipationFormData | null = null;

  async mounted() {
    await this.loadParticipation();
  }

  async loadParticipation() {
    this.part = await admin.getContestParticipation(
      this.contestUuid,
      this.participationId,
    );
    this.data = {
      user_id: this.part.user.id,
      cms_id: this.part.cms_id,
      manual_password: this.part.manual_password,
    };
  }

  async updateParticipation(data: ParticipationFormData) {
    this.$emit("submit", data);
    this.$emit("close");
  }
}
</script>
