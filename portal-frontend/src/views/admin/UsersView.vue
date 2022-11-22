<template>
  <AdminCard>
    <template v-slot:title> <b-icon icon="account" />&nbsp;Users </template>

    <div v-if="users === null">
      <b-skeleton width="20%" animated></b-skeleton>
      <b-skeleton width="40%" animated></b-skeleton>
      <b-skeleton width="80%" animated></b-skeleton>
      <b-skeleton animated></b-skeleton>
    </div>

    <b-field grouped group-multiline>
      <b-checkbox v-model="showEmail">
        Email
      </b-checkbox>
      <b-checkbox v-model="showCMS">
        CMS Username
      </b-checkbox>
      <b-checkbox v-model="showGroups">
        Groups
      </b-checkbox>
      <b-checkbox v-model="showAdmin">
        Admin
      </b-checkbox>
      <b-checkbox v-model="showCreatedAt">
        Created At
      </b-checkbox>
      <b-checkbox v-model="showBirthday">
        Birthday
      </b-checkbox>
      <b-checkbox v-model="showSchool">
        School
      </b-checkbox>
    </b-field>

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

    <b-table :data="users" hoverable default-sort="id" v-if="users !== null" :mobile-cards="false"
      @click="row => $router.push({ name: 'AdminUser', params: { userId: row.id }})"
      class="is-clickable"
    >
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
        :visible="showEmail"
      >
        {{ props.row.email }}
      </b-table-column>
      <b-table-column
        field="cms_username"
        label="CMS Username"
        sortable
        :searchable="searchable"
        v-slot="props"
        :visible="showCMS"
      >
        {{ props.row.cms_username === null ? "N/A" : props.row.cms_username }}
      </b-table-column>
      <b-table-column label="Groups" v-slot="props" width="200"
        :visible="showGroups">
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
      <b-table-column field="is_admin" label="Admin" centered v-slot="props"
        :visible="showAdmin">
        <b-icon icon="check" v-if="props.row.is_admin" />
        <b-icon icon="times" v-else />
      </b-table-column>
      <b-table-column
        field="created_at"
        label="Created At"
        sortable
        v-slot="props"
        :visible="showCreatedAt"
      >
        {{ props.row.created_at }}
      </b-table-column>
      <b-table-column
        field="birthday"
        label="Birthday"
        sortable
        v-slot="props"
        :visible="showBirthday"
      >
        {{ props.row.birthday }}
      </b-table-column>
      <b-table-column
        field="phone_nr"
        label="Phone Nr"
        sortable
        :searchable="searchable"
        v-slot="props"
        :visible="showPhoneNr"
      >
        {{ props.row.phone_nr }}
      </b-table-column>
      <b-table-column
        field="school_name"
        label="School"
        sortable
        :searchable="searchable"
        v-slot="props"
        :visible="showSchool"
      >
        {{ props.row.school_name }}
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
  showEmail = true;
  showCMS = true;
  showGroups = false;
  showAdmin = false;
  showCreatedAt = false;
  showBirthday = false;
  showPhoneNr = false;
  showSchool = true;

  async loadUsers() {
    this.users = await admin.getUsers();
  }

  async mounted() {
    await this.loadUsers();
  }
}
</script>
