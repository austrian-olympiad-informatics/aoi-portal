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

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import admin from "@/services/admin";
import { AdminUser, AdminUsers } from "@/types/admin";

export interface GroupFormData {
  name: string;
  description: string;
  users: number[];
}

const data = defineModel<GroupFormData>({ required: true });

const users = ref<AdminUsers | null>(null);
const filterText = ref("");

onMounted(async () => {
  users.value = await admin.getUsers();
});

function onTyping(text: string) {
  filterText.value = text;
}

const filteredUsers = computed<AdminUser[]>(() => {
  const uids = new Set(data.value.users);
  const search = filterText.value.toLowerCase();
  return users.value!.filter(
    (u) =>
      !uids.has(u.id) &&
      (search === "" ||
        u.first_name.toLowerCase().includes(search) ||
        u.last_name.toLowerCase().includes(search) ||
        u.email.toLowerCase().includes(search)),
  );
});

const selectedUsers = computed<AdminUser[]>({
  get: () => {
    const idToUser = new Map(users.value!.map((u) => [u.id, u]));
    return data.value.users.map((i) => idToUser.get(i)!);
  },
  set: (selected: AdminUser[]) => {
    data.value.users = selected.map((u) => u.id);
  },
});
</script>
