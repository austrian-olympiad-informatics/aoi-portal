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
      <b-field label="CMS Deleted">
        <b-switch v-model="data.deleted" disabled>Deleted</b-switch>
      </b-field>
    </b-field>
    <b-field grouped group-multiline label="CMS SSO">
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

    <b-field label="URL (CMS Contest URL)">
      <b-input v-model="data.url" />
    </b-field>

    <b-field label="Name">
      <b-input v-model="data.name" />
    </b-field>
    <b-field label="Teaser">
      <RichTextEditor v-model="data.teaser" />
    </b-field>
    <b-field label="Description">
      <RichTextEditor v-model="data.description" class="description-editor" />
    </b-field>

    <b-field label="Open Signup">
      <b-switch v-model="data.open_signup">Open Signup</b-switch>
    </b-field>
    <b-field label="Quali Round">
      <b-switch v-model="data.quali_round">Quali Round</b-switch>
    </b-field>
    <b-field label="Archived">
      <b-switch v-model="data.archived">Archived</b-switch>
    </b-field>
    <b-field label="Order Priority">
      <b-slider
        v-model="data.order_priority"
        indicator
        :tooltip="false"
        :min="-100"
        :max="100"
        format="raw"
      ></b-slider>
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
  </section>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { AdminGroups } from "@/types/admin";
import { PropType } from "vue";
import { Component, VModel, Vue } from "vue-property-decorator";
import RichTextEditor from "@/components/RichTextEditor.vue";

export interface ContestFormData {
  cms_id: number;
  cms_name: string;
  cms_description: string;
  cms_allow_sso_authentication: boolean;
  cms_sso_secret_key: string;
  cms_sso_redirect_url: string;
  url: string;
  open_signup: boolean;
  quali_round: boolean;
  name: string;
  teaser: string;
  description: string;
  archived: boolean;
  deleted: boolean;
  order_priority: number;
  auto_add_to_group_id: number | null;
}

@Component({
  components: {
    RichTextEditor,
  }
})
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

<style scoped>
.description-editor {
  min-height: 400px;
}
</style>
