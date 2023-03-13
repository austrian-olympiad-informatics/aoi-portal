<template>
  <form @submit.prevent="submit">
    <div class="modal-card" style="width: auto">
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

<script lang="ts">
import admin from "@/services/admin";
import { AdminGroups } from "@/types/admin";
import { Component, Vue } from "vue-property-decorator";

@Component
export default class ContestAddFromGroupModal extends Vue {
  groups: AdminGroups | null = null;
  selected: number | null = null;
  randomPasswords = false;

  async loadGroups() {
    this.groups = await admin.getGroups();
  }

  async mounted() {
    await this.loadGroups();
  }
  submit() {
    this.$emit("submit", {
      selected: this.selected,
      randomPasswords: this.randomPasswords,
    });
    this.$emit("close");
  }
}
</script>
