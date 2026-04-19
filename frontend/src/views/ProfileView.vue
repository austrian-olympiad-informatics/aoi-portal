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
          Wir benötigen diese Informationen um deine Schule nach einer
          Freistellung vom Unterricht für die Dauer der Trainingswochen und
          Wettbewerben zu fragen.
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

      <b-field label="Teilnahmeberechtigt">
        <section>
          <b-field>
            <b-radio v-model="eligibility"
                name="eligibility"
                native-value="ioi">
                Ich bin ein Schüler(m) an einer Österreichischen Schule und werde am nächsten 1. Juli nicht älter als 20 Jahre sein und bin somit teilnahmeberechtigt für die IOI.
            </b-radio>
          </b-field>
          <b-field>
            <b-radio v-model="eligibility"
                name="eligibility"
                native-value="ioi_egoi">
                Ich bin Schülerin(f/d) an einer Österreichischen Schule und werde am nächsten 1. Juli nicht älter als 20 Jahre sein und bin somit teilnahmeberechtigt für IOI und EGOI.
            </b-radio>
          </b-field>
          <b-field>
            <b-radio v-model="eligibility"
                name="eligibility"
                native-value="none">
                Ich bin bin nicht teilnahmeberechtigt und will mir nur die Aufgaben ansehen.
            </b-radio>
          </b-field>
        </section>
      </b-field>

      <b-button type="is-primary" native-type="submit" expanded class="mt-5"
        >Speichern</b-button
      >
    </form>
  </center-box-layout>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onMounted } from "vue";
import { useToast } from "buefy";
import profileService from "@/services/profile";
import CenterBoxLayout from "@/components/CenterBoxLayout.vue";

const toast = useToast();

const email = ref("");
const firstName = ref("");
const lastName = ref("");
const birthday = ref<Date | null>(null);
const phoneNr = ref<string | null>(null);
const addressStreet = ref<string | null>(null);
const addressZip = ref<string | null>(null);
const addressTown = ref<string | null>(null);
const schoolName = ref<string | null>(null);
const schoolAddress = ref<string | null>(null);
const eligibility = ref<string | null>(null);
const missingFields = ref<string[]>([]);

function calcMissingFields() {
  const missing: string[] = [];
  if (!birthday.value) missing.push("Geburtstag");
  if (!phoneNr.value) missing.push("Telefonnummer");
  if (!addressStreet.value) missing.push("Straße und Hausnummer");
  if (!addressZip.value) missing.push("PLZ");
  if (!addressTown.value) missing.push("Wohnort");
  if (!schoolName.value) missing.push("Name der Schule");
  if (!schoolAddress.value) missing.push("Adresse der Schule");
  if (!eligibility.value) missing.push("Teilnahmeberechtigung");
  missingFields.value = missing;
}

async function submit() {
  let bstring = null;
  if (birthday.value !== null) {
    bstring = `${birthday.value.getFullYear()}-${
      birthday.value.getMonth() + 1
    }-${birthday.value.getDate()}`;
  }
  await profileService.updateProfile({
    first_name: firstName.value,
    last_name: lastName.value,
    birthday: bstring,
    phone_nr: phoneNr.value || null,
    address_street: addressStreet.value || null,
    address_zip: addressZip.value || null,
    address_town: addressTown.value || null,
    school_name: schoolName.value || null,
    school_address: schoolAddress.value || null,
    eligibility: eligibility.value,
  });
  await loadProfile();
  toast.open({
    message: "Profil wurde aktualisiert!",
    type: "is-success",
  });
}

async function loadProfile() {
  const data = await profileService.profileInfo();
  email.value = data.email;
  firstName.value = data.first_name;
  lastName.value = data.last_name;
  birthday.value = data.birthday ? new Date(data.birthday) : null;
  phoneNr.value = data.phone_nr;
  addressStreet.value = data.address_street;
  addressZip.value = data.address_zip;
  addressTown.value = data.address_town;
  schoolName.value = data.school_name;
  schoolAddress.value = data.school_address;
  eligibility.value = data.eligibility;
  calcMissingFields();
}

onMounted(async () => {
  await loadProfile();
});
</script>
