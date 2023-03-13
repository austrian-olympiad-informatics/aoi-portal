<template>
  <AdminCard>
    <template v-slot:title>
      <b-icon icon="account-plus" />&nbsp;Create User</template
    >
    <form @submit.prevent="submit">
      <UserForm v-model="data" :password-required="true" />
      <b-button type="is-primary" native-type="submit">Create</b-button>
    </form>
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import AdminCard from "@/components/admin/AdminCard.vue";
import UserForm, { UserFormData } from "@/components/admin/UserForm.vue";
import admin from "@/services/admin";

@Component({
  components: {
    AdminCard,
    UserForm,
  },
})
export default class UserCreateView extends Vue {
  data: UserFormData = {
    first_name: "",
    last_name: "",
    password: null,
    email: "",
    is_admin: false,
    birthday: null,
    phone_nr: null,
    address_street: null,
    address_zip: null,
    address_town: null,
    school_name: null,
    school_address: null,
    cms_id: null,
    cms_username: null,
    groups: [],
  };
  async submit() {
    await admin.createUser({
      first_name: this.data.first_name,
      last_name: this.data.last_name,
      email: this.data.email,
      password: this.data.password!,
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
    });
    this.$buefy.toast.open({
      message: "User has been added!",
      type: "is-success",
    });
    this.$router.push({ name: "AdminUsers" });
  }
}
</script>
