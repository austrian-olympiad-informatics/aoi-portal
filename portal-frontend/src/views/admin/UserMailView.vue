<template>
  <div>
    <h1 class="title">Send Mail to Users</h1>

    <form @submit.prevent="submit">
      <b-field label="Subject">
        <b-input v-model="subject" required />
      </b-field>
      <b-field label="Reply To">
        <div>
          <div v-for="(rt, index) in reply_to" :key="index">
            <b-field>
              <b-input placeholder="Name" v-model="rt.name" required />
              <b-input
                placeholder="Email Address"
                v-model="rt.email"
                type="email"
                required
              />
              <b-button
                icon-right="delete"
                @click="reply_to.splice(index, 1)"
              />
            </b-field>
          </div>
          <b-button
            @click="reply_to.push({ email: '', name: '' })"
            icon-left="plus"
          >
            Add Reply To
          </b-button>
        </div>
      </b-field>
      <b-field label="Recipients">
        <div>
          <b-taginput
            v-model="selectedRecipients"
            :data="filteredRecipients"
            open-on-focus
            autocomplete
            v-if="users !== null"
            ref="taginput"
            class="recipient-input"
          >
            <template v-slot="props">
              {{ props.option.first_name }} {{ props.option.last_name }} ({{
                props.option.email
              }})
            </template>
            <template #selected="props">
              <b-tag
                v-for="(tag, index) in props.tags"
                :key="index"
                :tabstop="false"
                closable
                @close="$refs.taginput.removeTag(index, $event)"
              >
                {{ tag.first_name }} {{ tag.last_name }} ({{ tag.email }})
              </b-tag>
            </template>
          </b-taginput>
          <b-button @click="addFromContest" icon-left="plus">
            Add From Contest
          </b-button>
          <b-button @click="addFromGroup" icon-left="plus">
            Add From Group
          </b-button>
        </div>
      </b-field>

      <b-field label="Content">
        <RichTextEditor v-model="content" class="mail-editor" />
      </b-field>

      <hr />

      <h3 class="is-size-3">Preview</h3>
      <div class="preview">
        <div class="preview-inside">
          <div class="preview-wrapper">
            <div class="content" v-html="previewContent"></div>
            <div class="preview-bottom">
              &copy; Österreichische Informatikolympiade
            </div>
          </div>
        </div>
      </div>

      <hr />

      <b-button
        type="is-primary"
        expanded
        native-type="submit"
        :loading="loading"
        >Send Emails</b-button
      >
    </form>
  </div>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { AdminUser, AdminUsers } from "@/types/admin";
import { Component, Vue } from "vue-property-decorator";
import RichTextEditor from "@/components/RichTextEditor.vue";
import UserAddFromContestModal from "@/components/admin/UserAddFromContestModal.vue";
import UserAddFromGroupModal from "@/components/admin/UserAddFromGroupModal.vue";

interface Address {
  email: string;
  name: string;
}

@Component({
  components: {
    RichTextEditor,
  },
})
export default class UserMailView extends Vue {
  subject = "";
  reply_to: Address[] = [];
  recipients: number[] = [];
  content = "";
  loading = false;

  users: AdminUsers | null = null;

  async loadUsers() {
    this.users = await admin.getUsers();
  }

  async mounted() {
    await this.loadUsers();
  }
  async doAddFromContest(contestUuid: string) {
    const contest = await admin.getContest(contestUuid);
    const uids = contest.participations
      .map((p) => p.user.id)
      .filter((uid) => !this.recipients.includes(uid));
    this.recipients.push(...uids);
  }
  async doAddFromGroup(groupId: number) {
    const group = await admin.getGroup(groupId);
    const uids = group.users
      .map((u) => u.id)
      .filter((uid) => !this.recipients.includes(uid));
    this.recipients.push(...uids);
  }

  addFromContest() {
    this.$buefy.modal.open({
      parent: this,
      component: UserAddFromContestModal,
      hasModalCard: true,
      trapFocus: true,
      events: {
        submit: (val: string) => this.doAddFromContest(val),
      },
    });
  }

  addFromGroup() {
    this.$buefy.modal.open({
      parent: this,
      component: UserAddFromGroupModal,
      hasModalCard: true,
      trapFocus: true,
      events: {
        submit: (val: number) => this.doAddFromGroup(val),
      },
    });
  }

  async submit() {
    this.loading = true;
    try {
      await admin.userEmail({
        recipients: this.recipients,
        subject: this.subject,
        content: this.content,
        reply_to: this.reply_to,
      });
    } finally {
      this.loading = false;
    }
    this.$buefy.toast.open({
      message: "Email has been sent!",
      type: "is-success",
    });
  }

  get filteredRecipients(): AdminUser[] {
    const uids = new Set(this.recipients);
    return this.users!.filter((u) => !uids.has(u.id));
  }
  get selectedRecipients(): AdminUser[] {
    const idToUser = new Map(this.users!.map((u) => [u.id, u]));
    return this.recipients.map((i) => idToUser.get(i)!);
  }
  set selectedRecipients(selected: AdminUser[]) {
    this.recipients = selected.map((u) => u.id);
  }

  get previewContent(): string {
    return this.content
      .replaceAll("%VORNAME%", "Tom")
      .replaceAll("%NACHNAME%", "Rainer");
  }
}
</script>

<style scoped>
.mail-editor {
  min-height: 400px;
}
.preview {
  background-color: white;
  font-size: 13pt;
}
.preview-inside {
  font-family: BlinkMacSystemFont, -apple-system, "Segoe UI", "Roboto", "Oxygen",
    "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue",
    "Helvetica", "Arial", sans-serif;
  color: #4a4a4a;
  font-size: 1em;
  font-weight: 400;
  line-height: 1.5;
}
.preview-wrapper {
  background: #dddddd;
  padding: 15px;
}

.preview-bottom {
  background: #8a151b;
  color: #ffffff;
  padding: 40px 20px;
  font-size: 10pt;
}
.preview-bottom a {
  color: #93a9de;
  text-decoration: underline;
}
.preview .content {
  background: #ffffff;
  padding: 40px;
  text-align: justify;
  line-height: 1.3;
}
</style>
