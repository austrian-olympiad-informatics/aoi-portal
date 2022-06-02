<template>
  <div></div>
</template>

<script lang="ts">
import { CheckNotificationsParams } from "@/types/cms";
import cms from "@/services/cms";
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class CheckNotifications extends Vue {
  @Prop({
    type: String,
  })
  contestName!: string;

  lastNotification: string | null = null;
  checkNotificationsHandle: number | null = null;
  hasNotificationPermission = false;

  showNotification(subject: string, body: string) {
    this.$buefy.notification.open({
      message: `
          <h3 class="title is-5">${subject}</h3>
          <p>
            ${body}
          </p>
        `,
      type: "is-link",
      closable: true,
      hasIcon: true,
      indefinite: true,
    });
    if (this.hasNotificationPermission) {
      new Notification(subject, {
        body: body,
        icon: require("@/assets/logo.png"),
      });
    }
  }

  async checkNotifications(doShow: boolean) {
    const req: CheckNotificationsParams = {};
    if (this.lastNotification !== null)
      req.last_notification = this.lastNotification;
    const resp = await cms.checkNotifications(this.contestName, req);
    const allDts = [
      ...resp.new_announcements.map((x) => x.timestamp),
      ...resp.new_messages.map((x) => x.timestamp),
      ...resp.new_replies.map((x) => x.reply!.timestamp),
    ];
    for (const dts of allDts) {
      const dt = new Date(dts);
      if (
        this.lastNotification === null ||
        dt.getTime() > new Date(this.lastNotification).getTime()
      )
        this.lastNotification = dts;
    }
    if (!doShow) return;
    for (const ann of resp.new_announcements) {
      this.showNotification(`Neue Ankündigung - ${ann.subject}`, ann.text);
      this.$emit("new-announcement", ann);
    }
    for (const msg of resp.new_messages) {
      this.showNotification(`Neue Nachricht - ${msg.subject}`, msg.text);
      this.$emit("new-message", msg);
    }
    for (const q of resp.new_replies) {
      this.showNotification(`Frage Beantwortet - ${q.subject}`, q.reply!.text);
      this.$emit("new-reply", q);
    }
    if (
      resp.new_announcements.length ||
      resp.new_messages.length ||
      resp.new_replies.length
    ) {
      this.$emit("new-notification");
    }
  }

  async mounted() {
    await this.checkNotifications(false);
    this.checkNotificationsHandle = setInterval(async () => {
      await this.checkNotifications(true);
    }, 15000);
    if ("Notification" in window) {
      window.Notification.requestPermission().then(() => {
        this.hasNotificationPermission = true;
      });
    }
  }

  destroyed() {
    if (this.checkNotificationsHandle !== null)
      clearInterval(this.checkNotificationsHandle);
  }
}
</script>
