<template>
  <AdminCard>
    <template v-slot:title>
      <div class="level mb-0">
        <div class="level-left">
          <div class="level-item">
            <b-icon icon="medal" />&nbsp; Contest&nbsp;
            <span v-if="contest !== null">
              {{ contest.cms_name }}
            </span>
          </div>
        </div>
        <div class="level-right" v-if="contest !== null">
          <div class="level-item">
            <b-button
              tag="router-link"
              icon-left="medal"
              :to="{
                name: 'CMSAdminContest',
                params: { contestId: contest.cms_id },
              }"
            >
              Info
            </b-button>
          </div>
        </div>
      </div>
    </template>
    <div class="block">
      <h3 class="title is-4">Edit Contest</h3>
      <form @submit.prevent="updateContest(data)" v-if="data !== null">
        <ContestForm v-model="data" />
        <b-button type="is-primary" native-type="submit">Save</b-button>
      </form>
    </div>

    <div class="block" v-if="contest !== null">
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <p class="subtitle is-5">
              <strong>Actions</strong>
            </p>
          </div>
        </div>
        <div class="level-right">
          <div class="lebel-item buttons">
            <b-button icon-left="refresh" @click="refreshCMS">
              Refresh from CMS
            </b-button>
            <b-button
              icon-left="check"
              @click="provisionSSO"
              v-if="!contest.cms_allow_sso_authentication"
            >
              Provision SSO
            </b-button>
            <b-button
              icon-left="close"
              @click="removeSSO"
              v-if="contest.cms_allow_sso_authentication"
            >
              Remove SSO
            </b-button>
            <b-button icon-left="plus" @click="addFromGroup">
              Add Users From Group
            </b-button>
          </div>
        </div>
      </div>
    </div>

    <div class="block" v-if="contest !== null">
      <hr />
      <h3 class="title is-4">Participants</h3>

      <nav class="level">
        <!-- Left side -->
        <div class="level-left">
          <div class="level-item">
            <p class="subtitle is-5">
              <strong>{{ contest.participations.length }}</strong> Participants
            </p>
          </div>
        </div>
        <div class="level-right">
          <p class="level-item">
            <b-button
              icon-left="account-plus"
              @click="createParticipation"
              label="Add Participant"
            />
          </p>
        </div>
      </nav>

      <b-table
        :data="contest.participations"
        hoverable
        default-sort="id"
        :mobile-cards="false"
      >
        <b-table-column label="Name" v-slot="props">
          <router-link
            :to="{
              name: 'AdminUser',
              params: { userId: props.row.user.id },
            }"
          >
            {{ props.row.user.first_name }} {{ props.row.user.last_name }}
          </router-link>
        </b-table-column>
        <b-table-column label="Manual Password" v-slot="props">
          <template v-if="props.row.manual_password">
            <code>{{ props.row.manual_password }}</code>
          </template>
          <template v-else> No password </template>
        </b-table-column>

        <b-table-column label="Actions" width="100" centered v-slot="props">
          <a @click="updateParticipation(props.row.id)">
            <b-icon icon="pencil" />
          </a>
          <a @click="removeParticipation(props.row.id)">
            <b-icon icon="delete" />
          </a>
        </b-table-column>
      </b-table>
    </div>
  </AdminCard>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import { useRoute } from "vue-router";
import { useToast, useDialog, useModal } from "buefy";
import admin from "@/services/admin";
import { AdminContestDetail, AdminContestUpdateParams } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import ContestForm, {
  ContestFormData,
} from "@/components/admin/ContestForm.vue";
import ParticipationCreateModal from "@/components/admin/ParticipationCreateModal.vue";
import ParticipationUpdateModal from "@/components/admin/ParticipationUpdateModal.vue";
import ContestAddFromGroupModal from "@/components/admin/ContestAddFromGroupModal.vue";
import { ParticipationFormData } from "@/components/admin/ParticipationForm.vue";

const route = useRoute();
const toast = useToast();
const dialog = useDialog();
const modal = useModal();

const contestUuid = ref("");
const contest = ref<AdminContestDetail | null>(null);
const data = ref<ContestFormData | null>(null);

onMounted(async () => {
  contestUuid.value = route.params.contestUuid as string;
  await loadContest();
});

async function loadContest() {
  contest.value = await admin.getContest(contestUuid.value);
  data.value = {
    cms_id: contest.value.cms_id,
    cms_name: contest.value.cms_name,
    cms_description: contest.value.cms_description,
    cms_allow_sso_authentication: contest.value.cms_allow_sso_authentication,
    cms_sso_secret_key: contest.value.cms_sso_secret_key,
    cms_sso_redirect_url: contest.value.cms_sso_redirect_url,
    cms_allow_frontendv2: contest.value.cms_allow_frontendv2,
    url: contest.value.url,
    open_signup: contest.value.open_signup,
    quali_round: contest.value.quali_round,
    name: contest.value.name,
    teaser: contest.value.teaser,
    description: contest.value.description,
    archived: contest.value.archived,
    deleted: contest.value.deleted,
    order_priority: contest.value.order_priority,
    auto_add_to_group_id:
      contest.value.auto_add_to_group == null
        ? null
        : contest.value.auto_add_to_group.id,
  };
}

async function updateContest(formData: ContestFormData) {
  const params: AdminContestUpdateParams = {
    open_signup: formData.open_signup,
    auto_add_to_group_id: formData.auto_add_to_group_id,
    url: formData.url,
    name: formData.name,
    teaser: formData.teaser,
    description: formData.description,
    quali_round: formData.quali_round,
    archived: formData.archived,
    order_priority: formData.order_priority,
  };
  await admin.updateContest(contestUuid.value, params);
  toast.open({
    message: "Contest has been updated!",
    type: "is-success",
  });
}

async function provisionSSO() {
  if (!contest.value?.url) {
    toast.open({
      message: "Contest URL must be set to provision SSO!",
      type: "is-danger",
    });
    return;
  }
  await admin.contestProvisionSSO(contestUuid.value);
  await loadContest();
}

async function removeSSO() {
  await admin.contestRemoveSSO(contestUuid.value);
  await loadContest();
}

async function refreshCMS() {
  await admin.refreshCMSContests();
  await loadContest();
  toast.open({
    message: "Contest loaded from CMS!",
    type: "is-success",
  });
}

async function doCreateParticipation(formData: ParticipationFormData) {
  await admin.createContestParticipation(contestUuid.value, {
    user_id: formData.user_id!,
    cms_id: formData.cms_id ? +formData.cms_id : null,
    manual_password: formData.manual_password ? formData.manual_password : null,
  });
  await loadContest();
  toast.open({
    message: "Participant has been added!",
    type: "is-success",
  });
}

function createParticipation() {
  modal.open({
    component: ParticipationCreateModal,
    hasModalCard: true,
    trapFocus: true,
    events: {
      submit: (formData: ParticipationFormData) => {
        doCreateParticipation(formData);
      },
    },
  });
}

async function doUpdateParticipation(id: number, formData: ParticipationFormData) {
  await admin.updateContestParticipation(contestUuid.value, id, {
    cms_id: formData.cms_id!,
    manual_password: formData.manual_password || null,
  });
  await loadContest();
  toast.open({
    message: "Participant has been updated!",
    type: "is-success",
  });
}

function updateParticipation(id: number) {
  modal.open({
    component: ParticipationUpdateModal,
    props: {
      contestUuid: contestUuid.value,
      participationId: id,
    },
    hasModalCard: true,
    trapFocus: true,
    events: {
      submit: (formData: ParticipationFormData) => {
        doUpdateParticipation(id, formData);
      },
    },
  });
}

function removeParticipation(id: number) {
  dialog.confirm({
    message: "Remove this participation?",
    onConfirm: async () => {
      await admin.deleteContestParticipation(contestUuid.value, id);
      toast.open({
        message: "Participant has been removed!",
        type: "is-success",
      });
      await loadContest();
    },
  });
}

async function doAddFromGroup(selected: number, randomPasswords: boolean) {
  await admin.contestImportGroup(contestUuid.value, {
    group_id: selected,
    random_manual_passwords: randomPasswords,
  });
  await loadContest();
  toast.open({
    message: "Group has been added!",
    type: "is-success",
  });
}

function addFromGroup() {
  modal.open({
    component: ContestAddFromGroupModal,
    hasModalCard: true,
    trapFocus: true,
    events: {
      submit: (val: { selected: number; randomPasswords: boolean }) =>
        doAddFromGroup(val.selected, val.randomPasswords),
    },
  });
}
</script>
