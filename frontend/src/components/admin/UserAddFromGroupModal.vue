<template>
  <form @submit.prevent="submit">
    <div class="modal-card" style="width: auto">
      <header class="modal-card-head">
        <p class="modal-card-title">Add From Group</p>
        <button type="button" class="delete" @click="$emit('close')" />
      </header>
      <section class="modal-card-body">
        <b-select placeholder="Select a group" required v-model="selected">
          <option v-for="group in groups" :value="group.id" :key="group.id">
            {{ group.name }}
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
import { AdminGroups } from "@/types/admin";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class UserAddFromGroupModal extends Vue {
  groups: AdminGroups | null = null;
  selected: number | null = null;

  async loadGroups() {
    this.groups = await admin.getGroups();
  }

  async mounted() {
    await this.loadGroups();
  }
  submit() {
    this.$emit("submit", this.selected);
    this.$emit("close");
  }
}
</script>
