<template>
  <section>
    <div class="columns">
      <aside class="menu column is-2">
        <p class="menu-label">Admin Panel</p>
        <ul class="menu-list">
          <li>
            <router-link
              :to="{ name: 'AdminSettings' }"
              active-class="is-active"
            >
              <b-icon icon="cog" size="is-small" />&nbsp; Settings
            </router-link>
          </li>
          <li>
            <router-link :to="{ name: 'AdminUsers' }" active-class="is-active">
              <b-icon icon="account" size="is-small" />&nbsp; Users
            </router-link>
          </li>
          <li>
            <router-link
              :to="{ name: 'AdminContests' }"
              active-class="is-active"
            >
              <b-icon icon="medal" size="is-small" />&nbsp; Contests
            </router-link>
          </li>
          <li>
            <router-link :to="{ name: 'AdminGroups' }" active-class="is-active">
              <b-icon icon="account-group" size="is-small" />&nbsp; Groups
            </router-link>
          </li>
          <li>
            <router-link
              :to="{ name: 'AdminUserMail' }"
              active-class="is-active"
            >
              <b-icon icon="email" size="is-small" />&nbsp; User Mail
            </router-link>
          </li>
          <li>
            <router-link
              :to="{ name: 'AdminNewsletter' }"
              active-class="is-active"
            >
              <b-icon icon="email-newsletter" size="is-small" />&nbsp;
              Newsletter
            </router-link>
          </li>
        </ul>
      </aside>

      <div class="column is-10">
        <router-view></router-view>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class IndexView extends Vue {}
</script>

<style scoped>
section {
  padding: 2rem 1.5rem;
}
</style>
