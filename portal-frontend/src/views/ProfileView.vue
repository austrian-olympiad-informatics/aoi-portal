<template>
  <center-box-layout>
    <form @submit.prevent="submit">
      <h1 class="title is-3 mb-3">Profil</h1>

      <b-message
        type="is-warning"
        has-icon
        v-if="missingFields.length"
        class="content"
      >
        Die folgenden Felder müssen noch ausgefüllt werden, damit du dich für
        Trainingscamps und den Bundesbewerb qualifizieren kannst:
        <ul>
          <li v-for="field in missingFields" :key="field">
            {{ field }}
          </li>
        </ul>

        <p>
          Wir benötigen diese Informationen um deine Schule nach einer Freistellung vom Unterricht
          für die Dauer der Trainingswochen und Wettbewerben zu fragen.
        </p>
      </b-message>

      <b-field grouped group-multiline class="mb-5">
        <b-field label="E-Mail-Adresse">
          <b-input v-model="email" disabled />
          <p class="control">
            <b-button
              type="is-warning is-light"
              outlined
              tag="router-link"
              :to="{ name: 'ChangeEmail' }"
            >
              Ändern</b-button
            >
          </p>
        </b-field>
        <b-field label="Passwort">
          <b-button
            type="is-warning is-light"
            outlined
            tag="router-link"
            :to="{ name: 'ChangePassword' }"
          >
            Passwort ändern</b-button
          >
        </b-field>
      </b-field>

      <b-field label="Vorname">
        <b-input v-model="firstName" required />
      </b-field>
      <b-field label="Nachname">
        <b-input v-model="lastName" required />
      </b-field>

      <b-field label="Geburstdatum">
        <b-datepicker
          v-model="birthday"
          placeholder="Dein Geburstdatum"
          icon="calendar-today"
          :icon-right="birthday !== null ? 'close-circle' : ''"
          icon-right-clickable
          @icon-right-click="birthday = null"
          trap-focus
        />
      </b-field>
      <b-field label="Telefonnummer">
        <b-input v-model="phoneNr" placeholder="Deine Telefonnummer"></b-input>
      </b-field>

      <b-field label="Straße und Hausnummer">
        <b-input
          v-model="addressStreet"
          placeholder="Deine Straße und Hausnummer"
        ></b-input>
      </b-field>
      <b-field label="PLZ">
        <b-input v-model="addressZip" placeholder="1234"></b-input>
      </b-field>
      <b-field label="Wohnort">
        <b-input v-model="addressTown" placeholder="Dein Wohnort"></b-input>
      </b-field>

      <b-field label="Name der Schule">
        <b-input v-model="schoolName" placeholder="Schule"></b-input>
      </b-field>
      <b-field label="Adresse der Schule">
        <b-input
          v-model="schoolAddress"
          placeholder="Adresse der Schule"
        ></b-input>
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded class="mt-5"
        >Speichern</b-button
      >
    </form>
  </center-box-layout>
</template>

<script lang="ts">
import profile from "@/services/profile";
import { Component, Vue } from "vue-property-decorator";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

@Component({
  components: {
    CenterBoxLayout,
  },
})
export default class ProfileView extends Vue {
  email = "";
  firstName = "";
  lastName = "";
  birthday: Date | null = null;
  phoneNr: string | null = null;
  addressStreet: string | null = null;
  addressZip: string | null = null;
  addressTown: string | null = null;
  schoolName: string | null = null;
  schoolAddress: string | null = null;
  missingFields: string[] = [];

  calcMissingFields() {
    const missing: string[] = [];
    if (!this.birthday) missing.push("Geburtstag");
    if (!this.phoneNr) missing.push("Telefonnummer");
    if (!this.addressStreet) missing.push("Straße und Hausnummer");
    if (!this.addressZip) missing.push("PLZ");
    if (!this.addressTown) missing.push("Wohnort");
    if (!this.schoolName) missing.push("Name der Schule");
    if (!this.schoolAddress) missing.push("Adresse der Schule");
    this.missingFields = missing;
  }

  async submit() {
    let bstring = null;
    if (this.birthday !== null) {
      bstring = `${this.birthday.getFullYear()}-${this.birthday.getMonth()+1}-${this.birthday.getDate()}`;
    }
    await profile.updateProfile({
      first_name: this.firstName,
      last_name: this.lastName,
      birthday: bstring,
      phone_nr: this.phoneNr || null,
      address_street: this.addressStreet || null,
      address_zip: this.addressZip || null,
      address_town: this.addressTown || null,
      school_name: this.schoolName || null,
      school_address: this.schoolAddress || null,
    });
    await this.loadProfile();
    this.$buefy.toast.open({
      message: "Profil wurde aktualisiert!",
      type: "is-success",
    });
  }
  async loadProfile() {
    const data = await profile.profileInfo();
    this.email = data.email;
    this.firstName = data.first_name;
    this.lastName = data.last_name;
    this.birthday = data.birthday ? new Date(data.birthday) : null;
    this.phoneNr = data.phone_nr;
    this.addressStreet = data.address_street;
    this.addressZip = data.address_zip;
    this.addressTown = data.address_town;
    this.schoolName = data.school_name;
    this.schoolAddress = data.school_address;
    this.calcMissingFields();
  }
  async mounted() {
    await this.loadProfile();
  }
}
</script>
