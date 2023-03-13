<template>
  <AdminCard>
    <template v-slot:title> <b-icon icon="plus" />&nbsp;Create Group</template>
    <form @submit.prevent="createGroup(data)">
      <GroupForm v-model="data" />
      <b-button type="is-primary" native-type="submit">Create</b-button>
    </form>
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import AdminCard from "@/components/admin/AdminCard.vue";
import GroupForm, { GroupFormData } from "@/components/admin/GroupForm.vue";
import admin from "@/services/admin";

@Component({
  components: {
    AdminCard,
    GroupForm,
  },
})
export default class GroupCreateView extends Vue {
  data: GroupFormData = {
    name: "",
    description: "",
    users: [],
  };

  async createGroup(data: GroupFormData) {
    await admin.createGroup({
      name: data.name,
      description: data.description,
      users: data.users,
    });
    this.$buefy.toast.open({
      message: "Group has been added!",
      type: "is-success",
    });
    this.$router.push({ name: "AdminGroups" });
  }
}
</script>
