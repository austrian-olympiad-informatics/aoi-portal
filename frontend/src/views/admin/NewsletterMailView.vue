<template>
  <div>
    <h1 class="title">Send Newsletter</h1>

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

      <b-field label="Content">
        <RichTextEditor v-model="content" class="mail-editor" />
      </b-field>

      <hr />

      <h3 class="title is-4">Preview</h3>
      <div class="preview">
        <div class="preview-inside">
          <div class="preview-wrapper">
            <div class="content" v-html="content"></div>
            <div class="preview-bottom">
              &copy; Österreichische Informatikolympiade
              <p><a href="#">Newsletter abbestellen</a></p>
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
        >Send Newsletter</b-button
      >
    </form>
  </div>
</template>

<script lang="ts">
import admin from "@/services/admin";
import { Component, Vue } from "vue-property-decorator";
import RichTextEditor from "@/components/RichTextEditor.vue";

interface Address {
  email: string;
  name: string;
}

@Component({
  components: {
    RichTextEditor,
  },
})
export default class NewsletterMailView extends Vue {
  subject = "";
  reply_to: Address[] = [];
  content = "";
  loading = false;

  async submit() {
    this.loading = true;
    try {
      await admin.newsletterEmail({
        subject: this.subject,
        content: this.content,
        reply_to: this.reply_to,
      });
    } finally {
      this.loading = false;
    }
    this.$buefy.toast.open({
      message: "Newsletter has been sent!",
      type: "is-success",
    });
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
