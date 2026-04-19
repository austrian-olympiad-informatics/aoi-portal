<template>
  <section>
    <b-field label="Vorname">
      <b-input placeholder="Dein Vorname" v-model="data.first_name" required />
    </b-field>
    <b-field label="Nachname">
      <b-input placeholder="Dein Nachname" v-model="data.last_name" required />
    </b-field>
    <b-field label="E-Mail-Adresse">
      <b-input
        type="email"
        placeholder="Deine E-Mail-Adresse"
        v-model="data.email"
        required
      />
    </b-field>
    <b-field label="Passwort" class="mb-4">
      <b-input
        type="password"
        placeholder="********"
        v-model="data.password"
        minlength="8"
        required
      />
    </b-field>
    <b-field>
      <b-checkbox required>
        Ich stimme den
        <a href="https://informatikolympiade.at/datenschutz.html"
          >Datenschutzbestimmungen</a
        >
        zu.
      </b-checkbox>
    </b-field>
  </section>
</template>

<script setup lang="ts">
export interface RegisterInputData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

const data = defineModel<RegisterInputData>({ required: true });
</script>

<style scoped></style>
