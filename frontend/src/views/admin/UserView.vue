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

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "buefy";
import admin from "@/services/admin";
import { AdminUserUpdateParams, AdminUserDetail } from "@/types/admin";
import UserForm, { UserFormData } from "@/components/admin/UserForm.vue";
import AdminCard from "@/components/admin/AdminCard.vue";

const route = useRoute();
const router = useRouter();
const toast = useToast();

const userId = ref(0);
const user = ref<AdminUserDetail | null>(null);
const data = ref<UserFormData | null>(null);

onMounted(async () => {
  userId.value = +route.params.userId;
  await loadUser();
});

async function loadUser() {
  user.value = await admin.getUser(userId.value);
  data.value = {
    first_name: user.value.first_name,
    last_name: user.value.last_name,
    email: user.value.email,
    password: null,
    is_admin: user.value.is_admin,
    birthday: user.value.birthday,
    phone_nr: user.value.phone_nr,
    address_street: user.value.address_street,
    address_zip: user.value.address_zip,
    address_town: user.value.address_town,
    school_name: user.value.school_name,
    school_address: user.value.school_address,
    cms_id: user.value.cms_id,
    cms_username: user.value.cms_username,
    groups: user.value.groups.map((g) => g.id),
  };
}

async function deleteUser() {
  await admin.deleteUser(userId.value);
  toast.open({
    message: "User has been deleted!",
    type: "is-success",
  });
  router.push({ name: "AdminUsers" });
}

async function submit() {
  if (data.value === null) return;
  const params: AdminUserUpdateParams = {
    first_name: data.value.first_name,
    last_name: data.value.last_name,
    email: data.value.email,
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
  };
  if (data.value.password) {
    params.password = data.value.password;
  }
  await admin.updateUser(userId.value, params);
  toast.open({
    message: "User has been updated!",
    type: "is-success",
  });
}
</script>
