<template>
  <div class="wrapper" @animationend="onAnimationEnd">
    <div>
      <h1 class="title is-2">{{ headerText }}</h1>
      <img
        :src="memeUrl"
        loading="lazy"
        class="meme-img"
        @load="memeUrlLoaded"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import confetti from "canvas-confetti";

@Component
export default class SuccessModal extends Vue {
  @Prop({
    type: String,
  })
  headerText!: string;
  @Prop({ type: String, default: null })
  memeUrl!: string | null;

  onAnimationEnd() {
    this.showConfetti();
  }
  memeUrlLoaded() {
    if (this.memeUrl !== null) URL.revokeObjectURL(this.memeUrl);
  }
  showConfetti() {
    const count = 200;
    const defaults = {
      origin: { y: 0.9 },
    };

    const fire = (
      particleRatio: number,
      opts: {
        spread: number;
        startVelocity?: number;
        decay?: number;
        scalar?: number;
      }
    ) => {
      confetti(
        Object.assign({}, defaults, opts, {
          particleCount: Math.floor(count * particleRatio),
        })
      );
    };

    fire(0.25, {
      spread: 26,
      startVelocity: 55,
    });
    fire(0.2, {
      spread: 60,
    });
    fire(0.35, {
      spread: 100,
      decay: 0.91,
      scalar: 0.8,
    });
    fire(0.1, {
      spread: 120,
      startVelocity: 25,
      decay: 0.92,
      scalar: 1.2,
    });
    fire(0.1, {
      spread: 120,
      startVelocity: 45,
    });
  }
}
</script>

<style scoped>
.wrapper {
  display: flex;
  justify-content: center;
  color: rgb(237, 237, 237) !important;
  text-align: center;
}
h1 {
  color: rgb(237, 237, 237);
}
.meme-img {
  max-width: 60vw;
  height: 50vh;
  object-fit: contain;
  margin-left: auto;
  margin-right: auto;
  display: block;
}

.wrapper {
  animation-timing-function: ease-in;
  animation-duration: 1s;
  animation-delay: 0.7s;
  animation-name: successFade;
  animation-fill-mode: backwards;
}

@keyframes successFade {
  0% {
    opacity: 0;
    transform: scale(0.9, 0.9);
  }
  70% {
    opacity: 1;
    transform: scale(1, 1);
  }
  100% {
    opacity: 1;
    transform: scale(1, 1);
  }
}
</style>
