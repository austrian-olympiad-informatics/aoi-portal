<template>
  <section>
    <b-field label="User">
      <b-autocomplete
        :data="users"
        :disabled="!userEditable"
        :loading="users === null"
        :value="userValue"
        field="id"
        :custom-formatter="formatUser"
        required
        open-on-focus
        @select="u => data.user_id = u.id"
        >
      </b-autocomplete>
    </b-field>

    <b-field label="CMS ID">
      <NumberInput v-model="data.cms_id" />
    </b-field>
    <b-field label="Manual Password">
      <b-input v-model="data.manual_password"></b-input>
    </b-field>
  </section>
</template>

<script lang="ts">
import { Component, Prop, VModel, Vue } from "vue-property-decorator";
import { AdminUser, AdminUsers } from "@/types/admin";
import NumberInput from "../common/NumberInput.vue";
import admin from "@/services/admin";
import { PropType } from "vue";

export interface ParticipationFormData {
  user_id: number | null;
  cms_id: number | null;
  manual_password: string | null;
}

@Component({
  components: {
    NumberInput,
  },
})
export default class ParticipationForm extends Vue {
  @VModel({
    type: Object as PropType<ParticipationFormData>,
  })
  data!: ParticipationFormData;

  @Prop({
    default: false,
  })
  userEditable!: boolean;

  users: AdminUsers | null = null;

  formatUser(user: AdminUser): string {
    return `${user.first_name} ${user.last_name} (${user.email})`;
  }

  get userValue(): string {
    if (this.data.user_id === null || this.users === null)
      return "";
    const uidMap = new Map(this.users.map(u => [u.id, u]));
    return this.formatUser(uidMap.get(this.data.user_id)!);
  }

  async loadUsers() {
    this.users = await admin.getUsers();
  }

  async mounted() {
    await this.loadUsers();
  }
}
</script>

<style scoped></style>
