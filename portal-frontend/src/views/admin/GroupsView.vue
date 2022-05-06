<template>
  <AdminCard :loading="groups === null">
    <template v-slot:title>
      <b-icon icon="account-group" />&nbsp;Groups
    </template>

    <template v-if="groups !== null">

      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <p class="subtitle is-5">
              <strong>{{ groups.length }}</strong> Groups
            </p>
          </div>
        </div>
        <div class="level-right">
          <p class="level-item">
            <b-button
              icon-left="plus"
              tag="router-link"
              :to="{ name: 'AdminGroupCreate' }"
              >Add Group</b-button
            >
          </p>
        </div>
      </div>

      <div class="groups-container">
        <div v-for="group in groups" :key="group.id">
          <div class="card">
            <div class="card-content is-clearfix">
              <p class="title is-4 mb-3">
                {{ group.name }}
              </p>
              <ul class="mb-2">
                <li>
                  <span class="icon-text">
                    <b-icon icon="account-multiple"/>&nbsp;{{ group.user_count }} Users
                  </span>
                </li>
              </ul>
              <div class="content mb-1">
                {{ group.description }}
              </div>
              <div class="buttons is-pulled-right">
                <b-button icon-left="delete" @click="deleteGroup(group.id)"
                  >Delete</b-button
                >
                <b-button
                  tag="router-link"
                  icon-left="pencil"
                  :to="{
                    name: 'AdminGroup',
                    params: { groupId: group.id },
                  }"
                  >Edit</b-button
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { AdminGroups } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import admin from "@/services/admin";

@Component({
  components: {
    AdminCard,
  },
})
export default class GroupsView extends Vue {
  groups: AdminGroups | null = null;

  async loadGroups() {
    this.groups = await admin.getGroups();
  }

  async mounted() {
    await this.loadGroups();
  }
}
</script>

<style scoped>
.groups-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.icon-text {
  gap: 0.25rem;
}
</style>