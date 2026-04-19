<template>
  <div></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useNotification } from "buefy";
import { CheckNotificationsParams } from "@/types/cms";
import cms from "@/services/cms";

const props = defineProps<{ contestName: string }>();

const emit = defineEmits<{
  "new-announcement": [unknown];
  "new-message": [unknown];
  "new-reply": [unknown];
  "new-notification": [];
}>();

const notification = useNotification();

const lastNotification = ref<string | null>(null);

function showNotification(subject: string, body: string) {
  notification.open({
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
  if (
    "Notification" in window &&
    window.Notification.permission === "granted"
  ) {
    new Notification(subject, {
      body: body,
      icon: require("@/assets/logo.png"),
    });
  }
}

async function checkNotifications(doShow: boolean) {
  const req: CheckNotificationsParams = {};
  if (lastNotification.value !== null)
    req.last_notification = lastNotification.value;
  const resp = await cms.checkNotifications(props.contestName, req);
  const allDts = [
    ...resp.new_announcements.map((x) => x.timestamp),
    ...resp.new_messages.map((x) => x.timestamp),
    ...resp.new_replies.map((x) => x.reply!.timestamp),
  ];
  for (const dts of allDts) {
    const dt = new Date(dts);
    if (
      lastNotification.value === null ||
      dt.getTime() > new Date(lastNotification.value).getTime()
    )
      lastNotification.value = dts;
  }
  if (!doShow) return;
  for (const ann of resp.new_announcements) {
    showNotification(`Neue Ankündigung - ${ann.subject}`, ann.text);
    emit("new-announcement", ann);
  }
  for (const msg of resp.new_messages) {
    showNotification(`Neue Nachricht - ${msg.subject}`, msg.text);
    emit("new-message", msg);
  }
  for (const q of resp.new_replies) {
    showNotification(`Frage Beantwortet - ${q.subject}`, q.reply!.text);
    emit("new-reply", q);
  }
  if (
    resp.new_announcements.length ||
    resp.new_messages.length ||
    resp.new_replies.length
  ) {
    emit("new-notification");
  }
}

let checkNotificationsHandle: number | null = null;

onMounted(async () => {
  await checkNotifications(false);
  checkNotificationsHandle = window.setInterval(async () => {
    await checkNotifications(true);
  }, 15000);
});

onUnmounted(() => {
  if (checkNotificationsHandle !== null)
    clearInterval(checkNotificationsHandle);
});
</script>
