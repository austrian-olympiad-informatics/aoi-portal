<template>
  <AdminCard>
    <template v-slot:title> <b-icon icon="plus" />&nbsp;Create Group</template>
    <form @submit.prevent="createGroup(data)">
      <GroupForm v-model="data" />
      <b-button type="is-primary" native-type="submit">Create</b-button>
    </form>
  </AdminCard>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "buefy";
import AdminCard from "@/components/admin/AdminCard.vue";
import GroupForm, { GroupFormData } from "@/components/admin/GroupForm.vue";
import admin from "@/services/admin";

const router = useRouter();
const toast = useToast();

const data = ref<GroupFormData>({
  name: "",
  description: "",
  users: [],
});

async function createGroup(d: GroupFormData) {
  await admin.createGroup({
    name: d.name,
    description: d.description,
    users: d.users,
  });
  toast.open({
    message: "Group has been added!",
    type: "is-success",
  });
  router.push({ name: "AdminGroups" });
}
</script>
