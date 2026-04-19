<template>
  <section>
    <b-field label="User">
      <b-autocomplete
        :data="filteredUsers"
        :disabled="!userEditable"
        :loading="users === null"
        :value="userValue"
        field="id"
        :custom-formatter="formatUser"
        required
        open-on-focus
        @typing="onTyping"
        @select="(u) => (data.user_id = u.id)"
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

onMounted(async () => {
  users.value = await admin.getUsers();
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

const userValue = computed<string>(() => {
  if (data.value.user_id === null || users.value === null) return "";
  const uidMap = new Map(users.value.map((u) => [u.id, u]));
  return formatUser(uidMap.get(data.value.user_id)!);
});
</script>

<style scoped></style>
