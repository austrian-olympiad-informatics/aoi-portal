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

<script lang="ts">
import { Component, VModel, Vue } from "vue-property-decorator";
import { PropType } from "vue";

export interface LoginInputData {
  email: string;
  password: string;
}

@Component
export default class LoginForm extends Vue {
  @VModel({
    type: Object as PropType<LoginInputData>
  })
  data!: LoginInputData;
}
</script>

<style scoped></style>
