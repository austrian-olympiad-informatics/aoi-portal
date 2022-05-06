<template>
  <AdminCard>
    <template v-slot:title> <b-icon icon="account" />&nbsp;Users </template>

    <div v-if="users === null">
      <b-skeleton width="20%" animated></b-skeleton>
      <b-skeleton width="40%" animated></b-skeleton>
      <b-skeleton width="80%" animated></b-skeleton>
      <b-skeleton animated></b-skeleton>
    </div>

    <nav class="level" v-if="users !== null">
      <!-- Left side -->
      <div class="level-left">
        <div class="level-item">
          <p class="subtitle is-5">
            <strong>{{ users.length }}</strong> Users
          </p>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <b-switch v-model="searchable"><b-icon icon="magnify" /></b-switch>
        </div>
        <p class="level-item">
          <b-button
            icon-left="account-plus"
            tag="router-link"
            :to="{ name: 'AdminUserCreate' }"
          >
            Add User
          </b-button>
        </p>
      </div>
    </nav>

    <b-table :data="users" hoverable default-sort="id" v-if="users !== null">
      <b-table-column
        field="first_name"
        label="First Name"
        sortable
        :searchable="searchable"
        v-slot="props"
      >
        {{ props.row.first_name }}
      </b-table-column>
      <b-table-column
        field="last_name"
        label="Last Name"
        sortable
        :searchable="searchable"
        v-slot="props"
      >
        {{ props.row.last_name }}
      </b-table-column>
      <b-table-column
        field="email"
        label="Email"
        sortable
        :searchable="searchable"
        v-slot="props"
      >
        {{ props.row.email }}
      </b-table-column>
      <b-table-column
        field="cms_username"
        label="CMS Username"
        sortable
        :searchable="searchable"
        v-slot="props"
      >
        {{ props.row.cms_username === null ? "N/A" : props.row.cms_username }}
      </b-table-column>
      <b-table-column label="Groups" v-slot="props" width="200">
        <b-taglist>
          <b-tag v-for="group in props.row.groups" :key="group.id">
            <router-link
              :to="{
                name: 'AdminGroup',
                params: { groupId: group.id },
              }"
            >
              {{ group.name }}
            </router-link>
          </b-tag>
        </b-taglist>
      </b-table-column>
      <b-table-column field="is_admin" label="Admin" centered v-slot="props">
        <b-icon icon="check" v-if="props.row.is_admin" />
        <b-icon icon="times" v-else />
      </b-table-column>

      <b-table-column label="Actions" width="100" centered v-slot="props">
        <router-link
          :to="{ name: 'AdminUser', params: { userId: props.row.id } }"
        >
          <b-icon icon="pencil" type="is-dark" />
        </router-link>
      </b-table-column>
    </b-table>
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { AdminUsers } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import admin from "@/services/admin";

@Component({
  components: {
    AdminCard,
  },
})
export default class UsersView extends Vue {
  users: AdminUsers | null = null;
  searchable = false;

  async loadUsers() {
    this.users = await admin.getUsers();
  }

  async mounted() {
    await this.loadUsers();
  }
}
</script>
