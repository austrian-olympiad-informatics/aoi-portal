<template>
  <form @submit.prevent="submit">
    <div class="modal-card" style="width: auto">
      <header class="modal-card-head">
        <p class="modal-card-title">Teilnahmebedingungen</p>
        <button type="button" class="delete" @click="$emit('close')" />
      </header>
      <section class="modal-card-body">
        <b-checkbox required>
          Ich habe die
          <a href="https://v2.informatikolmypiade.at/TODO">
            Teilnahmebedingungen
          </a>
          gelesen und akzeptiere diese.
        </b-checkbox>
        <b-checkbox required>
          Ich verstehe, dass diese Qualifikation eine Einzelarbeit ist.
          Gruppenarbeiten sowie das Teilen von Lösungen sind nicht erlaubt.
        </b-checkbox>
      </section>
      <footer class="modal-card-foot">
        <b-button label="Abbrechen" @click="$emit('close')" />
        <b-button label="Bestätigen" type="is-primary" native-type="submit" />
      </footer>
    </div>
  </form>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class ConfirmRulesModal extends Vue {
  submit() {
    this.$emit("accepted");
    this.$emit("close");
  }
}
</script>
