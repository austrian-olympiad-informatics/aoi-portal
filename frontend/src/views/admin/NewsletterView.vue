<template>
  <div>
    <p class="title is-3"><b-icon icon="account" />&nbsp; Newsletter</p>

    <div v-if="subscribers === null">
      <b-skeleton width="20%" animated></b-skeleton>
      <b-skeleton width="40%" animated></b-skeleton>
      <b-skeleton width="80%" animated></b-skeleton>
      <b-skeleton animated></b-skeleton>
    </div>

    <nav class="level" v-if="subscribers !== null">
      <!-- Left side -->
      <div class="level-left">
        <div class="level-item">
          <p class="subtitle is-5">
            <strong>{{ subscribers.length }}</strong> Subscribers
          </p>
        </div>
      </div>
      <div class="level-right">
        <p class="level-item">
          <b-button
            icon-left="email"
            tag="router-link"
            :to="{
              name: 'AdminNewsletterMail',
            }"
          >
            Send Newsletter
          </b-button>
        </p>
      </div>
    </nav>

    <b-table
      :data="subscribers"
      hoverable
      v-if="subscribers !== null"
      :mobile-cards="false"
    >
      <b-table-column field="email" label="Email" sortable v-slot="props">
        {{ props.row.email }}
      </b-table-column>

      <b-table-column label="Actions" width="100" centered v-slot="props">
        <div class="is-clickable" @click="deleteSub(props.row.email)">
          <b-icon icon="delete" type="is-dark" />
        </div>
      </b-table-column>
    </b-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import { AdminNewsletterSubscribers } from "@/types/admin";
import AdminCard from "@/components/admin/AdminCard.vue";
import admin from "@/services/admin";

const subscribers = ref<AdminNewsletterSubscribers | null>(null);

async function loadNewsletter() {
  subscribers.value = await admin.getNewsletterSubscribers();
}

async function deleteSub(email: string) {
  await admin.deleteNewsletterSubscriber(email);
  await loadNewsletter();
}

onMounted(async () => {
  await loadNewsletter();
});
</script>
