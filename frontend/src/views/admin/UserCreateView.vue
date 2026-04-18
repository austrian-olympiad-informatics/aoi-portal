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

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "buefy";
import AdminCard from "@/components/admin/AdminCard.vue";
import UserForm, { UserFormData } from "@/components/admin/UserForm.vue";
import admin from "@/services/admin";

const router = useRouter();
const toast = useToast();

const data = ref<UserFormData>({
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
});

async function submit() {
  await admin.createUser({
    first_name: data.value.first_name,
    last_name: data.value.last_name,
    email: data.value.email,
    password: data.value.password!,
    is_admin: data.value.is_admin,
    birthday: data.value.birthday,
    phone_nr: data.value.phone_nr,
    address_street: data.value.address_street,
    address_zip: data.value.address_zip,
    address_town: data.value.address_town,
    school_name: data.value.school_name,
    school_address: data.value.school_address,
    cms_id: data.value.cms_id,
    cms_username: data.value.cms_username,
    groups: data.value.groups,
  });
  toast.open({
    message: "User has been added!",
    type: "is-success",
  });
  router.push({ name: "AdminUsers" });
}
</script>
