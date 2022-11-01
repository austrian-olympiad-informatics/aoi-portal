<template>
  <section>
    <b-field grouped>
      <b-field label="First Name">
        <b-input v-model="data.first_name" required />
      </b-field>
      <b-field label="Last Name">
        <b-input v-model="data.last_name" required />
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="Email address">
        <b-input v-model="data.email" type="email" required />
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="Password">
        <b-input
          v-model="data.password"
          type="password"
          :required="passwordRequired"
        ></b-input>
      </b-field>

      <b-field label="Is Admin">
        <b-switch v-model="data.is_admin">Is Admin</b-switch>
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="Birthday">
        <b-datepicker
          v-model="birthday"
          placeholder="Click to select..."
          icon="calendar-today"
          :icon-right="birthday !== null ? 'close-circle' : ''"
          icon-right-clickable
          @icon-right-click="birthday = null"
          trap-focus
        />
      </b-field>
      <b-field label="Phone Nr">
        <b-input v-model="data.phone_nr"></b-input>
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="Address Street">
        <b-input v-model="data.address_street"></b-input>
      </b-field>
      <b-field label="Address ZIP">
        <b-input v-model="data.address_zip"></b-input>
      </b-field>
      <b-field label="Address Town">
        <b-input v-model="data.address_town"></b-input>
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="School Name">
        <b-input v-model="data.school_name"></b-input>
      </b-field>
      <b-field label="School Address">
        <b-input v-model="data.school_address"></b-input>
      </b-field>
    </b-field>

    <b-field grouped>
      <b-field label="CMS ID">
        <NumberInput v-model="data.cms_id" />
      </b-field>
      <b-field label="CMS Username">
        <b-input v-model="data.cms_username"></b-input>
      </b-field>
    </b-field>

    <b-field label="Groups">
      <b-taginput
        v-model="selectedGroups"
        :data="filteredGroups"
        field="name"
        open-on-focus
        autocomplete
        v-if="groups !== null"
        ref="taginput"
      >
        <template #selected="props">
          <b-tag
            v-for="(tag, index) in props.tags"
            :key="index"
            :tabstop="false"
            closable
            @close="$refs.taginput.removeTag(index, $event)"
          >
            <router-link
              :to="{
                name: 'AdminGroup',
                params: { groupId: tag.id },
              }"
            >
              {{ tag.name }}
            </router-link>
          </b-tag>
        </template>
      </b-taginput>
    </b-field>
  </section>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { AdminGroup, AdminGroups } from "@/types/admin";
import { PropType } from "vue";
import { Component, Prop, Vue, VModel } from "vue-property-decorator";
import NumberInput from "../common/NumberInput.vue";

export interface UserFormData {
  first_name: string;
  last_name: string;
  password: string | null;
  email: string;
  is_admin: boolean;
  birthday: string | null;
  phone_nr: string | null;
  address_street: string | null;
  address_zip: string | null;
  address_town: string | null;
  school_name: string | null;
  school_address: string | null;
  cms_id: number | null;
  cms_username: string | null;
  groups: number[];
}

@Component({
  components: {
    NumberInput,
  },
})
export default class UserForm extends Vue {
  @VModel({
    type: Object as PropType<UserFormData>,
  })
  data!: UserFormData;

  @Prop({
    default: false,
  })
  readonly passwordRequired!: boolean;

  groups: AdminGroups | null = null;

  get birthday(): Date | null {
    if (this.data.birthday === null) return null;
    return new Date(this.data.birthday);
  }
  set birthday(date: Date | null) {
    if (this.birthday === null) {
      this.data.birthday = null;
      return;
    }
    this.data.birthday = `${this.birthday.getFullYear()}-${this.birthday.getMonth()+1}-${this.birthday.getDate()}`;
  }

  get filteredGroups(): AdminGroup[] {
    const gids = new Set(this.data.groups);
    return this.groups!.filter((g) => !gids.has(g.id));
  }
  get selectedGroups(): AdminGroup[] {
    const idToGroup = new Map(this.groups!.map((g) => [g.id, g]));
    return this.data.groups.map((i) => idToGroup.get(i)!);
  }
  set selectedGroups(selected: AdminGroup[]) {
    this.data.groups = selected.map((g) => g.id);
  }

  async loadGroups() {
    this.groups = await admin.getGroups();
  }

  async mounted() {
    await this.loadGroups();
  }
}
</script>

<style scoped></style>
