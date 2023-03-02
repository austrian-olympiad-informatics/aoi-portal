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

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import admin from "@/services/admin";
import { AdminGroupDetail, AdminGroupUpdateParams } from "@/types/admin";
import GroupForm, { GroupFormData } from "@/components/admin/GroupForm.vue";
import AdminCard from "@/components/admin/AdminCard.vue";

@Component({
  components: {
    AdminCard,
    GroupForm,
  },
})
export default class GroupView extends Vue {
  groupId!: number;
  group: AdminGroupDetail | null = null;
  data: GroupFormData | null = null;

  async mounted() {
    this.groupId = +this.$route.params.groupId;
    await this.loadGroup();
  }

  async loadGroup() {
    this.group = await admin.getGroup(this.groupId);
    this.data = {
      name: this.group.name,
      description: this.group.description,
      users: this.group.users.map((u) => u.id),
    };
  }

  async updateGroup(data: GroupFormData) {
    const params: AdminGroupUpdateParams = {
      name: data.name,
      description: data.description,
      users: data.users,
    };
    await admin.updateGroup(this.groupId, params);
    this.$buefy.toast.open({
      message: "Group has been updated!",
      type: "is-success",
    });
  }
}
</script>
