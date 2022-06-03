<template>
  <div class="hero is-fullheight-with-navbar">
    <div class="hero-body">
      <div class="welcome container has-text-centered">
        <img
          alt="Informatikolympiade Logo"
          src="@/assets/logo-big.png"
          class="aoi-logo"
          width="300"
          height="300"
          loading="lazy"
        />
        <h1 class="title">Österreichische Informatikolympiade</h1>
        <h2 class="subtitle">
          Melde dich an, um Trainingsaufgaben zu lösen und an
          Qualifikationsrunden teilzunehmen.
        </h2>

        <div class="buttons">
          <b-button
            type="is-primary is-large"
            tag="router-link"
            :to="{ name: 'Register' }"
            ><strong>Registrieren</strong></b-button
          >
          <b-button
            type="is-light is-large"
            tag="router-link"
            :to="{ name: 'Login' }"
            >Anmelden</b-button
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import "~bulma/sass/utilities/mixins";

.hero {
  /*min-height: calc(100vh - 6.5rem) !important;*/
  min-height: calc(100vh - 12.5rem) !important;
}
.aoi-logo {
  width: 250px;
  margin-bottom: 20px;
}
.welcome h1 {
  font-weight: 600;
  font-size: 4rem;
  margin-bottom: 2rem;
}
.welcome h2 {
  font-size: 1.5rem;
  margin-bottom: 2rem;
}
.welcome .buttons {
  justify-content: center;
  column-gap: 1rem;
}

@include mobile {
  .aoi-logo {
    width: 175px;
    margin-bottom: 15px;
  }
  .welcome h1 {
    font-size: 2rem;
  }
  .weclome h2 {
    font-size: 1.25rem;
  }
  .welcome .button {
    font-size: 1.25rem !important;
  }
}
</style>
