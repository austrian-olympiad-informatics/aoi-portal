<template>
  <section>
    <b-field label="Name">
      <b-input v-model="data.name" required />
    </b-field>
    <b-field label="Description">
      <b-input v-model="data.description" />
    </b-field>

    <b-field label="Members">
      <b-taginput
        v-model="selectedUsers"
        :data="filteredUsers"
        open-on-focus
        autocomplete
        v-if="users !== null"
        ref="taginput"
        @typing="onTyping"
      >
        <template v-slot="props">
          {{ props.option.first_name }} {{ props.option.last_name }} ({{
            props.option.email
          }})
        </template>
        <template #selected="props">
          <b-tag
            v-for="(tag, index) in props.tags"
            :key="index"
            :tabstop="false"
            closable
            @close="$refs.taginput.removeTag(index, $event)"
          >
            <router-link
              :to="{
                name: 'AdminUser',
                params: { userId: tag.id },
              }"
            >
              {{ tag.first_name }} {{ tag.last_name }} ({{ tag.email }})
            </router-link>
          </b-tag>
        </template>
      </b-taginput>
    </b-field>
  </section>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { AdminUser, AdminUsers } from "@/types/admin";
import { PropType } from "vue";
import {  Component, VModel, Vue, toNative } from "vue-facing-decorator";

export interface GroupFormData {
  name: string;
  description: string;
  users: number[];
}

@Component
class GroupForm extends Vue {
  @VModel({
    type: Object as PropType<GroupFormData>,
  })
  data!: GroupFormData;

  users: AdminUsers | null = null;
  filterText: string = "";

  async loadUsers() {
    this.users = await admin.getUsers();
  }

  async mounted() {
    await this.loadUsers();
  }

  onTyping(text: string) {
    this.filterText = text;
  }

  get filteredUsers(): AdminUser[] {
    const uids = new Set(this.data.users);
    const search = this.filterText.toLowerCase();
    return this.users!.filter(
      (u) =>
        !uids.has(u.id) &&
        (search === "" ||
          u.first_name.toLowerCase().includes(search) ||
          u.last_name.toLowerCase().includes(search) ||
          u.email.toLowerCase().includes(search)),
    );
  }
  get selectedUsers(): AdminUser[] {
    const idToUser = new Map(this.users!.map((u) => [u.id, u]));
    return this.data.users.map((i) => idToUser.get(i)!);
  }
  set selectedUsers(selected: AdminUser[]) {
    this.data.users = selected.map((u) => u.id);
  }
}
export default toNative(GroupForm)
</script>
