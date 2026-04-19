<template>
  <div>
    <div class="block">
      <h2 class="title is-3">Ankündigungen</h2>
      <b-switch
        class="mb-3"
        v-if="showNotificationSwitch"
        @input="askNotificationPermission"
        >Benachrichtigung bei neuen Ankündigungen</b-switch
      >
      <div v-if="!announcements.length">
        <i>Noch keine Ankündigungen</i>
      </div>
      <div v-else v-for="(ann, index) in announcements" :key="index">
        <b-message type="is-info" class="mb-3">
          <span class="is-pulled-right">{{ formatDate(ann.timestamp) }}</span>
          <h4 class="title is-6">{{ ann.subject }}</h4>
          <p class="notification-text content">
            {{ ann.text }}
          </p>
        </b-message>
      </div>
    </div>

    <div class="block" v-if="messages.length">
      <h2 class="title is-3">Nachrichten</h2>
      <div v-for="(msg, index) in messages" :key="index">
        <b-message type="is-info" class="mb-3">
          <span class="is-pulled-right">{{ formatDate(msg.timestamp) }}</span>
          <h4 class="title is-6">{{ msg.subject }}</h4>
          <p class="notification-text content">
            {{ msg.text }}
          </p>
        </b-message>
      </div>
    </div>

    <div class="block">
      <h2 class="title is-3">Fragen</h2>
      <form @submit.prevent="askQuestion" class="question-form">
        <b-field label="Betreff">
          <b-input v-model="questionSubject" placeholder="Betreff" required />
        </b-field>
        <b-field label="Text">
          <b-input v-model="questionText" type="textarea" required />
        </b-field>
        <b-button native-type="submit" type="is-primary" expanded
          >Frage stellen</b-button
        >
      </form>
      <div v-for="(q, index) in questions" :key="index">
        <b-message type="is-info" class="mb-3 is-relative">
          <span class="is-pulled-right">{{ formatDate(q.timestamp) }}</span>
          <h4 class="title is-6">{{ q.subject }}</h4>
          <p class="notification-text content">
            {{ q.text }}
          </p>
          <div v-if="q.reply" class="question-reply">
            <span class="is-pulled-right">{{
              formatDate(q.reply.timestamp)
            }}</span>
            <p class="notification-text content">
              {{ q.reply.text }}
            </p>
          </div>
          <div v-else class="question-reply">
            <i>Noch keine Antwort.</i>
          </div>
        </b-message>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import { useToast } from "buefy";
import { formatDateShort } from "@/util/dt";
import { Announcement, Message, Question } from "@/types/cms";
import cms from "@/services/cms";

const props = withDefaults(
  defineProps<{
    announcements: Announcement[];
    messages: Message[];
    questions: Question[];
    contestName: string;
    taskName?: string | null;
  }>(),
  {
    announcements: () => [],
    messages: () => [],
    questions: () => [],
    taskName: null,
  },
);

const emit = defineEmits<{ "new-question": [] }>();

const toast = useToast();

const questionSubject = ref("");
const questionText = ref("");
const showNotificationSwitch = ref(false);

function updateShowNotificationSwitch() {
  showNotificationSwitch.value =
    "Notification" in window && window.Notification.permission === "default";
}

function askNotificationPermission() {
  window.Notification.requestPermission().then(
    () => {
      updateShowNotificationSwitch();
      if (window.Notification.permission === "granted")
        toast.open({
          message:
            "Du erhälst jetzt bei neuen Ankündigungen eine Benachrichtigung",
          type: "is-success",
          duration: 5000,
        });
    },
    () => {
      updateShowNotificationSwitch();
    },
  );
}

onMounted(() => {
  updateShowNotificationSwitch();
});

function formatDate(date: string) {
  return formatDateShort(new Date(), new Date(date));
}

async function askQuestion() {
  if (props.taskName === null) {
    await cms.askQuestion(props.contestName, {
      subject: questionSubject.value,
      text: questionText.value,
    });
  } else {
    await cms.askQuestionTask(props.contestName, props.taskName, {
      subject: questionSubject.value,
      text: questionText.value,
    });
  }
  questionSubject.value = "";
  questionText.value = "";
  emit("new-question");
}
</script>

<style scoped>
.question-reply {
  border-top: 1px solid #3e8ed085;
  margin-top: 10px;
  padding-top: 10px;
}
.notification-text {
  white-space: pre-line;
}
.question-form {
  margin-bottom: 1.5rem;
  padding: 19px;
  background-color: #f5f5f5;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}
</style>
