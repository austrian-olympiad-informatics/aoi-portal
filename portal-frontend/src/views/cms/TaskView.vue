<template>
  <div class="task-wrap">
    <div class="task-container" v-if="task !== null">
      <div class="descr-column">
        <div class="descr-wrap">
          <DescriptionPanel
            :task="task"
            @submission-scored="onSubmissionScored"
            @reload-task="loadTask"
          />
        </div>
      </div>
      <div class="code-column">
        <router-view
          class="code-container"
          :task="task"
          :key="$route.fullPath"
          @new-submission="onNewSubmission"
        />
      </div>
    </div>

    <CheckNotifications :contest-name="contestName" @new-notification="loadTask" />
  </div>
</template>

<script lang="ts">
import { SubmissionShort, Task } from "@/types/cms";
import cms from "@/services/cms";
import { Component, Vue } from "vue-property-decorator";
import DescriptionPanel from "./DescriptionPanel.vue";
import CodePanel from "./CodePanel.vue";
import confetti from "canvas-confetti";
import CheckNotifications from "./CheckNotifications.vue";

@Component({
  components: {
    DescriptionPanel,
    CodePanel,
    CheckNotifications,
  },
})
export default class TaskView extends Vue {
  get contestName(): string {
    return this.$route.params.contestName;
  }
  get taskName(): string {
    return this.$route.params.taskName;
  }
  task: Task | null = null;

  async loadTask() {
    this.task = await cms.getTask(this.contestName, this.taskName);
  }
  async mounted() {
    await this.loadTask();
  }
  onNewSubmission(sub: SubmissionShort) {
    this.task?.submissions.push(sub);
  }
  async onSubmissionScored(sub: SubmissionShort) {
    if (this.task === null) return;
    const scoreBefore = this.task.score;
    await this.loadTask();
    const scoreAfter = this.task.score;
    if (scoreBefore != scoreAfter && scoreAfter >= this.task.max_score) {
      this.showConfetti();
    }
  }
  showConfetti() {
    const count = 200;
    const defaults = {
      origin: { y: 0.7 },
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
.task-wrap {
  height: 100%;
}
.task-container {
  flex: 1;
  display: flex;
  height: 100%;
}
.descr-column {
  flex: none;
  width: 33.33%;
  max-width: 600px;
  min-width: 370px;
  display: flex;
  flex-direction: column;
  border-right: 2px solid rgb(207, 207, 207);
}
.descr-wrap {
  flex-basis: 0;
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
}
.code-column {
  flex-grow: 1;
  flex-shrink: 0;
  flex-basis: auto;
  width: 66.67%;
  display: flex;
  flex-direction: column;
}
.code-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
