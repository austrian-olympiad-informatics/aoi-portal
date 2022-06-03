<template>
  <div>
    <div class="block">
      <h2 class="title is-3">Ankündigungen</h2>
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
            <span class="is-pulled-right">{{ formatDate(q.timestamp) }}</span>
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

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import { formatDateShort } from "@/util/dt";
import { Announcement, Message, Question } from "@/types/cms";
import cms from "@/services/cms";

@Component
export default class NotificationsSection extends Vue {
  @Prop({
    type: Array,
    default: () => [],
  })
  announcements!: Announcement[];

  @Prop({
    type: Array,
    default: () => [],
  })
  messages!: Message[];

  @Prop({
    type: Array,
    default: () => [],
  })
  questions!: Question[];

  @Prop({
    type: String,
  })
  contestName!: string;

  @Prop({
    type: String,
    default: null,
  })
  taskName!: string | null;

  questionSubject = "";
  questionText = "";

  formatDate(date: string) {
    return formatDateShort(new Date(), new Date(date));
  }

  async askQuestion() {
    if (this.taskName === null) {
      await cms.askQuestion(this.contestName, {
        subject: this.questionSubject,
        text: this.questionText,
      });
      this.$emit("new-question");
    } else {
      await cms.askQuestionTask(this.contestName, this.taskName, {
        subject: this.questionSubject,
        text: this.questionText,
      });
      this.$emit("new-question");
    }
  }
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
