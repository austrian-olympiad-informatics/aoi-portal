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

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import admin from "@/services/admin";
import { AdminGroup, AdminGroups } from "@/types/admin";
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

const data = defineModel<UserFormData>({ required: true });

const props = withDefaults(defineProps<{ passwordRequired?: boolean }>(), {
  passwordRequired: false,
});

const groups = ref<AdminGroups | null>(null);

onMounted(async () => {
  groups.value = await admin.getGroups();
});

const birthday = computed<Date | null>({
  get: () => {
    if (data.value.birthday === null) return null;
    return new Date(data.value.birthday);
  },
  set: (date: Date | null) => {
    if (date === null) {
      data.value.birthday = null;
      return;
    }
    data.value.birthday = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
  },
});

const filteredGroups = computed<AdminGroup[]>(() => {
  const gids = new Set(data.value.groups);
  return groups.value!.filter((g) => !gids.has(g.id));
});

const selectedGroups = computed<AdminGroup[]>({
  get: () => {
    const idToGroup = new Map(groups.value!.map((g) => [g.id, g]));
    return data.value.groups.map((i) => idToGroup.get(i)!);
  },
  set: (selected: AdminGroup[]) => {
    data.value.groups = selected.map((g) => g.id);
  },
});
</script>

<style scoped></style>
