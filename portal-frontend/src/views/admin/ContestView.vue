<template>
  <AdminCard>
    <template v-slot:title>
      <b-icon icon="medal" />&nbsp; Contest&nbsp;
      <span v-if="contest !== null">
        {{ contest.cms_name }}
      </span>
    </template>
    <div class="block">
      <h3 class="is-size-4">Edit Contest</h3>
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
            <b-button icon-left="refresh"> Refresh from CMS </b-button>
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
          </div>
        </div>
      </div>
    </div>

    <div class="block" v-if="contest !== null">
      <h3 class="is-size-4">Participants</h3>

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
              @click="isCreateParticipationModalActive = true"
              label="Add Participant"
            />
          </p>
        </div>
      </nav>

      <b-table :data="contest.participations" hoverable default-sort="id">
        <b-table-column label="Name" v-slot="props">
          <router-link :to="{
            name: 'AdminUser',
            params: { userId: props.row.id }
          }">
            {{ props.row.user.first_name }} {{ props.row.user.last_name }}
          </router-link>
        </b-table-column>
        <b-table-column label="Manual Password" v-slot="props">
          <template v-if="props.row.manual_password">
            <code>{{ props.row.manual_password }}</code>
          </template>
          <template v-else>
            No password
          </template>
        </b-table-column>

        <b-table-column label="Actions" width="100" centered v-slot="props">
          <a @click="updateParticipantModalId = props.row.id">
            <b-icon icon="pencil" />
          </a>
        </b-table-column>
      </b-table>
    </div>

    <b-modal
      v-model="isCreateParticipationModalActive"
      has-modal-card
      trap-focus
      :destroy-on-hide="false"
      aria-role="dialog"
      aria-label="Add Participant"
      close-button-aria-label="Close"
      aria-modal
    >
      <template #default="props">
        <ParticipationCreateModal
          :contest-uuid="contestUuid"
          @close="props.close"
        >
        </ParticipationCreateModal>
      </template>
    </b-modal>

    <b-modal
      :active="updateParticipantModalId !== null"
      @close="updateParticipantModalId = null"
      has-modal-card
      trap-focus
      :destroy-on-hide="false"
      aria-role="dialog"
      aria-label="Add Participant"
      close-button-aria-label="Close"
      aria-modal
    >
      <template #default="props">
        <ParticipationUpdateModal
          :contest-uuid="contestUuid"
          :participation-id="updateParticipantModalId"
          @close="props.close"
        >
        </ParticipationUpdateModal>
      </template>
    </b-modal>
  </AdminCard>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import admin from "@/services/admin";
import { AdminContestDetail, AdminContestUpdateParams } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import ContestForm, {
  ContestFormData,
} from "@/components/admin/ContestForm.vue";
import ParticipationCreateModal from "@/components/admin/ParticipationCreateModal.vue";
import ParticipationUpdateModal from "@/components/admin/ParticipationUpdateModal.vue";

@Component({
  components: {
    AdminCard,
    ContestForm,
    ParticipationCreateModal,
    ParticipationUpdateModal,
  },
})
export default class ContestView extends Vue {
  contestUuid!: string;
  contest: AdminContestDetail | null = null;
  data: ContestFormData | null = null;

  isCreateParticipationModalActive = false;
  updateParticipantModalId: number | null = null;

  async mounted() {
    this.contestUuid = this.$route.params.contestUuid;
    await this.loadContest();
  }

  async loadContest() {
    this.contest = await admin.getContest(this.contestUuid);
    this.data = {
      cms_id: this.contest.cms_id,
      cms_name: this.contest.cms_name,
      cms_description: this.contest.cms_description,
      cms_allow_sso_authentication: this.contest.cms_allow_sso_authentication,
      cms_sso_secret_key: this.contest.cms_sso_secret_key,
      cms_sso_redirect_url: this.contest.cms_sso_redirect_url,
      url: this.contest.url,
      public: this.contest.public,
      auto_add_to_group_id:
        this.contest.auto_add_to_group == null
          ? null
          : this.contest.auto_add_to_group.id,
    };
  }

  async updateContest(data: ContestFormData) {
    let params: AdminContestUpdateParams = {
      public: data.public,
      auto_add_to_group_id: data.auto_add_to_group_id,
      url: data.url,
    };
    await admin.updateContest(this.contestUuid, params);
    this.$buefy.toast.open({
      message: "Contest has been updated!",
      type: "is-success",
    });
  }

  async provisionSSO() {
    await admin.contestProvisionSSO(this.contestUuid);
    await this.loadContest();
  }
  async removeSSO() {
    await admin.contestRemoveSSO(this.contestUuid);
    await this.loadContest();
  }
}
</script>
