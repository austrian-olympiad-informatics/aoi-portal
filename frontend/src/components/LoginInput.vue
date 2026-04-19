<template>
  <section>
    <b-field label="E-Mail-Adresse">
      <b-input
        type="email"
        placeholder="z.B. alice@gmail.com"
        v-model="data.email"
        required
      />
    </b-field>
    <b-field label="Passwort" class="mb-4">
      <b-input
        type="password"
        placeholder="********"
        v-model="data.password"
        required
      />
    </b-field>
  </section>
</template>

<script setup lang="ts">
export interface LoginInputData {
  email: string;
  password: string;
}

const data = defineModel<LoginInputData>({ required: true });
</script>

<style scoped></style>
