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
          <b-button @click="downloadCSV" icon-left="plus">
            Download as CSV for Thunderbird
          </b-button>
        </div>
      </b-field>

      <b-field label="Content">
        <RichTextEditor v-model="content" class="mail-editor" />
      </b-field>

      <hr />

      <h3 class="title is-4">Preview</h3>
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

<script setup lang="ts">
import { ref, computed } from "vue";
import { onMounted } from "vue";
import { useToast, useModal } from "buefy";
import admin from "@/services/admin";
import { AdminUser, AdminUsers } from "@/types/admin";
import RichTextEditor from "@/components/RichTextEditor.vue";
import UserAddFromContestModal from "@/components/admin/UserAddFromContestModal.vue";
import UserAddFromGroupModal from "@/components/admin/UserAddFromGroupModal.vue";

interface Address {
  email: string;
  name: string;
}

const toast = useToast();
const modal = useModal();

const subject = ref("");
const reply_to = ref<Address[]>([]);
const recipients = ref<number[]>([]);
const content = ref("");
const loading = ref(false);
const users = ref<AdminUsers | null>(null);
const taginput = ref(null);

onMounted(async () => {
  users.value = await admin.getUsers();
});

const filteredRecipients = computed<AdminUser[]>(() => {
  const uids = new Set(recipients.value);
  return users.value!.filter((u) => !uids.has(u.id));
});

const selectedRecipients = computed<AdminUser[]>({
  get: () => {
    const idToUser = new Map(users.value!.map((u) => [u.id, u]));
    return recipients.value.map((i) => idToUser.get(i)!);
  },
  set: (selected: AdminUser[]) => {
    recipients.value = selected.map((u) => u.id);
  },
});

const previewContent = computed<string>(() =>
  content.value
    .replaceAll("%VORNAME%", "Tom")
    .replaceAll("%NACHNAME%", "Rainer"),
);

async function doAddFromContest(contestUuid: string) {
  const contest = await admin.getContest(contestUuid);
  const uids = contest.participations
    .map((p) => p.user.id)
    .filter((uid) => !recipients.value.includes(uid));
  recipients.value.push(...uids);
}

async function doAddFromGroup(groupId: number) {
  const group = await admin.getGroup(groupId);
  const uids = group.users
    .map((u) => u.id)
    .filter((uid) => !recipients.value.includes(uid));
  recipients.value.push(...uids);
}

function addFromContest() {
  modal.open({
    component: UserAddFromContestModal,
    hasModalCard: true,
    trapFocus: true,
    events: {
      submit: (val: string) => doAddFromContest(val),
    },
  });
}

function addFromGroup() {
  modal.open({
    component: UserAddFromGroupModal,
    hasModalCard: true,
    trapFocus: true,
    events: {
      submit: (val: number) => doAddFromGroup(val),
    },
  });
}

function downloadCSV() {
  const encodeRow = (row: string[]): string => {
    return row
      .map((s) => {
        s = s.replace(/"/g, '""');
        if (s.search(/("|,|\n)/g) >= 0) s = `"${s}"`;
        return s;
      })
      .join(",");
  };
  const rows = [["First Name", "Last Name", "Primary Email"]];
  rows.push(
    ...selectedRecipients.value.map((u) => [u.first_name, u.last_name, u.email]),
  );
  const csvContent = rows.map((r) => encodeRow(r)).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv" });
  const anchor = document.createElement("a");
  anchor.href = URL.createObjectURL(blob);
  anchor.download = "mailing-list.csv";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
}

async function submit() {
  loading.value = true;
  try {
    await admin.userEmail({
      recipients: recipients.value,
      subject: subject.value,
      content: content.value,
      reply_to: reply_to.value,
    });
  } finally {
    loading.value = false;
  }
  toast.open({
    message: "Email has been sent!",
    type: "is-success",
  });
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
  font-family:
    BlinkMacSystemFont,
    -apple-system,
    "Segoe UI",
    "Roboto",
    "Oxygen",
    "Ubuntu",
    "Cantarell",
    "Fira Sans",
    "Droid Sans",
    "Helvetica Neue",
    "Helvetica",
    "Arial",
    sans-serif;
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
