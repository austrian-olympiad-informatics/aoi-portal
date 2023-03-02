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
      <div class="code-column" ref="codeCol">
        <router-view
          class="code-container"
          :task="task"
          :key="$route.fullPath"
          @new-submission="onNewSubmission"
        />
      </div>
    </div>

    <CheckNotifications
      :contest-name="contestName"
      @new-notification="loadTask"
    />
  </div>
</template>

<script lang="ts">
import { ScoringGroup, SubmissionShort, Task } from "@/types/cms";
import cms from "@/services/cms";
import { Component, Vue } from "vue-property-decorator";
import DescriptionPanel from "./DescriptionPanel.vue";
import CodePanel from "./CodePanel.vue";
import CheckNotifications from "./CheckNotifications.vue";
import SuccessModal from "./SuccessModal.vue";

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

    let successModalText: string | null = null;

    if (this.task.scoring.type === "sum") {
      const scoreBefore = this.task.score;
      await this.loadTask();
      const scoreAfter = this.task.score;

      if (scoreBefore !== scoreAfter && scoreAfter >= this.task.max_score) {
        successModalText = "Aufgabe gelöst! 🎉";
      }
    } else {
      const calcScoreFractions = () => {
        return this.task!.score_subtasks!.map((x) => x.fraction);
      };
      const stBefore = calcScoreFractions();
      await this.loadTask();
      const stAfter = calcScoreFractions();
      const stSolved = [];
      for (let i = 0; i < stAfter.length; i++) {
        const x = stAfter[i];
        const y = i >= stBefore.length ? 0 : stBefore[i];
        if (x >= 1 && y < 1) stSolved.push(i + 1);
      }
      if (stSolved.length > 0) {
        successModalText = `Teilaufgabe ${stSolved.join(", ")} gelöst! 🎉`;
      }
    }

    if (successModalText !== null) {
      let memeUrl = null;
      if (sub.result.meme_digest !== null) {
        const blob = await cms.getSubmissionMeme(
          this.contestName,
          this.taskName,
          sub.uuid,
          sub.result.meme_digest
        );
        memeUrl = URL.createObjectURL(blob);
      }

      this.$buefy.modal.open({
        parent: this,
        component: SuccessModal,
        trapFocus: true,
        props: {
          headerText: successModalText,
          memeUrl: memeUrl,
        },
        animation: "success-modal",
      });
    }
  }
}
</script>

<style scoped lang="scss">
@import "~bulma/sass/utilities/mixins";

.task-wrap {
  height: 100%;
}
.task-container {
  display: flex;
  flex-direction: row;
  height: 100%;
}
@include touch {
  .task-container {
    flex-direction: column;
  }
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
@include touch {
  .descr-column {
    width: 100%;
    max-width: initial;
    min-width: initial;
  }
}
.descr-wrap {
  flex-basis: 0;
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
}
@include touch {
  .descr-wrap {
    overflow-y: initial;
  }
}
.code-column {
  flex-grow: 1;
  flex-shrink: 0;
  flex-basis: auto;
  width: 66.67%;
  display: flex;
  flex-direction: column;
}
@include touch {
  .code-column {
    width: 100%;
    height: auto;
    flex: initial;
    /* prevent layout jumping around when selecting a submission */
    min-height: 80vh;
  }
}
.code-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>

<style>
/* have to have some transition on transition element for it to know when it ends */
.success-modal-enter-active,
.success-modal-leave-active {
  transition: opacity 0.75s ease-in;
}
.success-modal-enter,
.success-modal-leave-to {
  opacity: 1;
}
.success-modal-enter-active .modal-background,
.success-modal-leave-active .modal-background {
  transition: opacity 0.75s ease-in;
}
.success-modal-enter .modal-background,
.success-modal-leave-to .modal-background {
  opacity: 0;
}
</style>
