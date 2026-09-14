<template>
  <AdminCard>
    <template v-slot:title>
      <b-icon icon="account-group" />&nbsp; Edit Group&nbsp;
      <span v-if="group !== null">
        {{ group.name }}
      </span>
    </template>
    <form @submit.prevent="updateGroup(data)" v-if="data !== null">
      <GroupForm v-model="data" />
      <b-button type="is-primary" native-type="submit">Update</b-button>
    </form>
  </AdminCard>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "buefy";
import admin from "@/services/admin";
import { AdminGroupDetail, AdminGroupUpdateParams } from "@/types/admin";
import GroupForm, { GroupFormData } from "@/components/admin/GroupForm.vue";
import AdminCard from "@/components/admin/AdminCard.vue";

const route = useRoute();
const toast = useToast();

const groupId = ref(0);
const group = ref<AdminGroupDetail | null>(null);
const data = ref<GroupFormData | null>(null);

onMounted(async () => {
  groupId.value = +route.params.groupId;
  await loadGroup();
});

async function loadGroup() {
  group.value = await admin.getGroup(groupId.value);
  data.value = {
    name: group.value.name,
    description: group.value.description,
    users: group.value.users.map((u) => u.id),
  };
}

async function updateGroup(formData: GroupFormData) {
  const params: AdminGroupUpdateParams = {
    name: formData.name,
    description: formData.description,
    users: formData.users,
  };
  await admin.updateGroup(groupId.value, params);
  toast.open({
    message: "Group has been updated!",
    type: "is-success",
  });
}
</script>
