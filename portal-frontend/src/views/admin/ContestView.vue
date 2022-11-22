<template>
  <AdminCard>
    <template v-slot:title>
      <b-icon icon="medal" />&nbsp; Contest&nbsp;
      <span v-if="contest !== null">
        {{ contest.cms_name }}
      </span>
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

      <b-table :data="contest.participations" hoverable default-sort="id" :mobile-cards="false">
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
import ContestAddFromGroupModal from "@/components/admin/ContestAddFromGroupModal.vue";
import { ParticipationFormData } from "@/components/admin/ParticipationForm.vue";

@Component({
  components: {
    AdminCard,
    ContestForm,
  },
})
export default class ContestView extends Vue {
  contestUuid!: string;
  contest: AdminContestDetail | null = null;
  data: ContestFormData | null = null;

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
      cms_allow_frontendv2: this.contest.cms_allow_frontendv2,
      url: this.contest.url,
      open_signup: this.contest.open_signup,
      quali_round: this.contest.quali_round,
      name: this.contest.name,
      teaser: this.contest.teaser,
      description: this.contest.description,
      archived: this.contest.archived,
      deleted: this.contest.deleted,
      order_priority: this.contest.order_priority,
      auto_add_to_group_id:
        this.contest.auto_add_to_group == null
          ? null
          : this.contest.auto_add_to_group.id,
    };
  }

  async updateContest(data: ContestFormData) {
    let params: AdminContestUpdateParams = {
      open_signup: data.open_signup,
      auto_add_to_group_id: data.auto_add_to_group_id,
      url: data.url,
      name: data.name,
      teaser: data.teaser,
      description: data.description,
      quali_round: data.quali_round,
      archived: data.archived,
      order_priority: data.order_priority,
    };
    await admin.updateContest(this.contestUuid, params);
    this.$buefy.toast.open({
      message: "Contest has been updated!",
      type: "is-success",
    });
  }

  async provisionSSO() {
    if (!this.contest?.url) {
      this.$buefy.toast.open({
        message: "Contest URL must be set to provision SSO!",
        type: "is-danger",
      });
      return;
    }
    await admin.contestProvisionSSO(this.contestUuid);
    await this.loadContest();
  }
  async removeSSO() {
    await admin.contestRemoveSSO(this.contestUuid);
    await this.loadContest();
  }
  async refreshCMS() {
    await admin.refreshCMSContests();
    await this.loadContest();
    this.$buefy.toast.open({
      message: "Contest loaded from CMS!",
      type: "is-success",
    });
  }
  async doCreateParticipation(data: ParticipationFormData) {
    await admin.createContestParticipation(this.contestUuid, {
      user_id: data.user_id!,
      cms_id: data.cms_id ? +data.cms_id : null,
      manual_password: data.manual_password ? data.manual_password : null,
    });
    await this.loadContest();
    this.$buefy.toast.open({
      message: "Participant has been added!",
      type: "is-success",
    });
  }
  async createParticipation() {
    this.$buefy.modal.open({
      parent: this,
      component: ParticipationCreateModal,
      hasModalCard: true,
      trapFocus: true,
      events: {
        submit: (data: ParticipationFormData) => {
          this.doCreateParticipation(data);
        },
      },
    });
  }
  async doUpdateParticipation(id: number, data: ParticipationFormData) {
    await admin.updateContestParticipation(this.contestUuid, id, {
      cms_id: data.cms_id!,
      manual_password: data.manual_password || null,
    });
    await this.loadContest();
    this.$buefy.toast.open({
      message: "Participant has been updated!",
      type: "is-success",
    });
  }
  async updateParticipation(id: number) {
    this.$buefy.modal.open({
      parent: this,
      component: ParticipationUpdateModal,
      props: {
        contestUuid: this.contestUuid,
        participationId: id,
      },
      hasModalCard: true,
      trapFocus: true,
      events: {
        submit: (data: ParticipationFormData) => {
          this.doUpdateParticipation(id, data);
        },
      },
    });
  }
  async removeParticipation(id: number) {
    this.$buefy.dialog.confirm({
      message: "Remove this participation?",
      onConfirm: async () => {
        await admin.deleteContestParticipation(this.contestUuid, id);
        this.$buefy.toast.open({
          message: "Participant has been removed!",
          type: "is-success",
        });
        await this.loadContest();
      },
    });
  }
  async doAddFromGroup(selected: number, randomPasswords: boolean) {
    await admin.contestImportGroup(this.contestUuid, {
      group_id: selected,
      random_manual_passwords: randomPasswords,
    });
    await this.loadContest();
    this.$buefy.toast.open({
      message: "Group has been added!",
      type: "is-success",
    });
  }
  async addFromGroup() {
    this.$buefy.modal.open({
      parent: this,
      component: ContestAddFromGroupModal,
      hasModalCard: true,
      trapFocus: true,
      events: {
        submit: (val: { selected: number; randomPasswords: boolean }) =>
          this.doAddFromGroup(val.selected, val.randomPasswords),
      },
    });
  }
}
</script>
