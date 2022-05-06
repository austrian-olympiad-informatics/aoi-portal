<template>
  <AdminCard>
    <template v-slot:title>
      <b-icon icon="account" />&nbsp; Edit User&nbsp;
      <span v-if="user !== null">
        {{ user.first_name }} {{ user.last_name }}
      </span>
    </template>
    <form @submit.prevent="submit" v-if="data !== null">
      <UserForm v-model="data" :password-required="false" />
      <b-button type="is-primary" native-type="submit">Update</b-button>
    </form>

    <b-button
      type="is-warning"
      class="is-pulled-right"
      icon-left="delete"
      @click="deleteUser"
      >Delete User</b-button
    >
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import admin from "@/services/admin";
import { AdminUserUpdateParams, AdminUserDetail } from "@/types/admin";
import UserForm, { UserFormData } from "@/components/admin/UserForm.vue";
import AdminCard from "@/components/admin/AdminCard.vue";

@Component({
  components: {
    AdminCard,
    UserForm,
  },
})
export default class UserView extends Vue {
  userId!: number;
  user: AdminUserDetail | null = null;
  data: UserFormData | null = null;

  async mounted() {
    this.userId = +this.$route.params.userId;
    await this.loadUser();
  }

  async loadUser() {
    this.user = await admin.getUser(this.userId);
    this.data = {
      first_name: this.user.first_name,
      last_name: this.user.last_name,
      email: this.user.email,
      password: null,
      is_admin: this.user.is_admin,
      birthday: this.user.birthday,
      phone_nr: this.user.phone_nr,
      address_street: this.user.address_street,
      address_zip: this.user.address_zip,
      address_town: this.user.address_town,
      school_name: this.user.school_name,
      school_address: this.user.school_address,
      cms_id: this.user.cms_id,
      cms_username: this.user.cms_username,
      groups: this.user.groups.map((g) => g.id),
    };
  }

  async deleteUser() {
    await admin.deleteUser(this.userId);
    this.$buefy.toast.open({
      message: "User has been deleted!",
      type: "is-success",
    });
    this.$router.push({ name: "AdminUsers" });
  }

  async submit() {
    if (this.data === null) return;
    let params: AdminUserUpdateParams = {
      first_name: this.data.first_name,
      last_name: this.data.last_name,
      email: this.data.email,
      is_admin: this.data.is_admin,
      birthday: this.data.birthday,
      phone_nr: this.data.phone_nr,
      address_street: this.data.address_street,
      address_zip: this.data.address_zip,
      address_town: this.data.address_town,
      school_name: this.data.school_name,
      school_address: this.data.school_address,
      cms_id: this.data.cms_id,
      cms_username: this.data.cms_username,
      groups: this.data.groups,
    };
    if (this.data.password) {
      params.password = this.data.password;
    }
    await admin.updateUser(this.userId, params);
    this.$buefy.toast.open({
      message: "User has been updated!",
      type: "is-success",
    });
  }
}
</script>
