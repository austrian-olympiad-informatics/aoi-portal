<template>
  <section>
    <b-field label="User">
      <b-autocomplete
        :data="filteredUsers"
        :disabled="!userEditable"
        :loading="users === null"
        v-model="inputText"
        field="id"
        :custom-formatter="formatUser"
        required
        open-on-focus
        @typing="onTyping"
        @select="(u) => (data.user_id = u?.id ?? null)"
      >
      </b-autocomplete>
    </b-field>

    <b-field label="CMS ID">
      <NumberInput v-model="data.cms_id" />
    </b-field>
    <b-field label="Manual Password">
      <b-input v-model="data.manual_password"></b-input>
    </b-field>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { AdminUser, AdminUsers } from "@/types/admin";
import NumberInput from "../common/NumberInput.vue";
import admin from "@/services/admin";

export interface ParticipationFormData {
  user_id: number | null;
  cms_id: number | null;
  manual_password: string | null;
}

const data = defineModel<ParticipationFormData>({ required: true });

const props = withDefaults(defineProps<{ userEditable?: boolean }>(), {
  userEditable: false,
});

const users = ref<AdminUsers | null>(null);
const filterText = ref("");
const inputText = ref("");

onMounted(async () => {
  users.value = await admin.getUsers();
  if (data.value.user_id !== null) {
    const user = users.value.find((u) => u.id === data.value.user_id);
    if (user) inputText.value = formatUser(user);
  }
});

function onTyping(text: string) {
  filterText.value = text;
}

const filteredUsers = computed<AdminUser[]>(() => {
  if (users.value === null) return [];
  const search = filterText.value.toLowerCase();
  if (search === "") return users.value;
  return users.value.filter(
    (u) =>
      u.first_name.toLowerCase().includes(search) ||
      u.last_name.toLowerCase().includes(search) ||
      u.email.toLowerCase().includes(search),
  );
});

function formatUser(user: AdminUser): string {
  return `${user.first_name} ${user.last_name} (${user.email})`;
}
</script>

<style scoped></style>
