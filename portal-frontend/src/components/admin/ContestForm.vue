<template>
  <section>
    <b-field grouped group-multiline label="CMS Properties">
      <b-field label="CMS ID">
        <b-input
          v-model="data.cms_id"
          inputmode="numeric"
          pattern="[0-9]*"
          disabled
        />
      </b-field>
      <b-field label="CMS Name">
        <b-input v-model="data.cms_name" disabled />
      </b-field>
      <b-field label="CMS Description">
        <b-input v-model="data.cms_description" disabled />
      </b-field>
      <b-field label="CMS Allow SSO">
        <b-switch
          v-model="data.cms_allow_sso_authentication"
          disabled
        ></b-switch>
      </b-field>
      <b-field label="CMS SSO Secret Key">
        <b-input v-model="data.cms_sso_secret_key" disabled />
      </b-field>
      <b-field label="CMS SSO Redirect URL">
        <b-input v-model="data.cms_sso_redirect_url" disabled />
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="Contest URL">
        <b-input v-model="data.url" />
      </b-field>

      <b-field label="Public">
        <b-switch v-model="data.public">Public</b-switch>
      </b-field>

      <b-field label="Auto Add Participants to Group">
        <b-select
          placeholder="Select a group"
          :loading="groups === null"
          :value="
            data.auto_add_to_group_id === null ? '' : data.auto_add_to_group_id
          "
          @input="onAutoaddInput"
        >
          <option value="">No Group</option>
          <template v-if="groups !== null">
            <option v-for="group in groups" :value="group.id" :key="group.id">
              {{ group.name }}
            </option>
          </template>
        </b-select>
      </b-field>
    </b-field>
  </section>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { AdminGroups } from "@/types/admin";
import { PropType } from "vue";
import { Component, VModel, Vue } from "vue-property-decorator";

export interface ContestFormData {
  cms_id: number;
  cms_name: string;
  cms_description: string;
  cms_allow_sso_authentication: boolean;
  cms_sso_secret_key: string;
  cms_sso_redirect_url: string;
  url: string;
  public: boolean;
  auto_add_to_group_id: number | null;
}

@Component
export default class ContestForm extends Vue {
  @VModel({
    type: Object as PropType<ContestFormData>,
  })
  data!: ContestFormData;

  groups: AdminGroups | null = null;

  async loadGroups() {
    this.groups = await admin.getGroups();
  }

  async mounted() {
    await this.loadGroups();
  }

  onAutoaddInput(event: InputEvent) {
    const val = (event.target as HTMLSelectElement).value;
    this.data.auto_add_to_group_id = val ? +val : null;
  }
}
</script>

<style scoped></style>
