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

<script lang="ts">
import { Component, VModel, Vue } from "vue-property-decorator";
import { PropType } from "vue";

export interface RegisterInputData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

@Component
export default class RegisterInput extends Vue {
  @VModel({
    type: Object as PropType<RegisterInputData>,
  })
  data!: RegisterInputData;
}
</script>

<style scoped></style>
