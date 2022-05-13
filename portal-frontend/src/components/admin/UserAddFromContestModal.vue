<template>
  <form @submit.prevent="submit">
    <div class="modal-card" style="width: auto">
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

<script lang="ts">
import admin from "@/services/admin";
import { AdminContests } from "@/types/admin";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class UserAddFromContestModal extends Vue {
  contests: AdminContests | null = null;
  selected: string | null = null;

  async loadContests() {
    this.contests = await admin.getContests();
  }

  async mounted() {
    await this.loadContests();
  }
  submit() {
    this.$emit("submit", this.selected);
    this.$emit("close");
  }
}
</script>
