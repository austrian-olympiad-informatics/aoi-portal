import http from "./common";
import {
  CheckNotificationsParams,
  CheckNotificationsResult,
  Contest,
  ContestTaskScores,
  QuestionParams,
  Submission,
  SubmissionShort,
  SubmitParams,
  SubmitResult,
  Task,
  UserEval,
  UserEvalSubmitParams,
  UserEvalSubmitResult,
} from "@/types/cms";

class CMSService {
  async getContest(contestName: string): Promise<Contest> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(contestName)}`,
    );
    return resp.data;
  }
  async getTask(contestName: string, taskName: string): Promise<Task> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}`,
    );
    return resp.data;
  }
  async getSubmission(
    contestName: string,
    taskName: string,
    submissionUuid: string,
  ): Promise<Submission> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/submission/${encodeURIComponent(
        submissionUuid,
      )}`,
    );
    return resp.data;
  }
  async getSubmissionShort(
    contestName: string,
    taskName: string,
    submissionUuid: string,
  ): Promise<SubmissionShort> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/submission/${encodeURIComponent(
        submissionUuid,
      )}/short`,
    );
    return resp.data;
  }
  async getStatement(
    contestName: string,
    taskName: string,
    language: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/statements/${encodeURIComponent(
        language,
      )}`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async getStatementHTML(
    contestName: string,
    taskName: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/statement-html`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async getDefaultInput(
    contestName: string,
    taskName: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/default-input`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async getAttachment(
    contestName: string,
    taskName: string,
    filename: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/attachments/${encodeURIComponent(
        filename,
      )}`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async getLanguageTemplate(
    contestName: string,
    taskName: string,
    filename: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(
        taskName,
      )}/language-template/${encodeURIComponent(filename)}`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async getSubmissionFile(
    contestName: string,
    taskName: string,
    submissionUuid: string,
    filename: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/submission/${encodeURIComponent(
        submissionUuid,
      )}/files/${encodeURIComponent(filename)}`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async getSubmissionMeme(
    contestName: string,
    taskName: string,
    submissionUuid: string,
    digest: string,
  ): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/submission/${encodeURIComponent(
        submissionUuid,
      )}/meme`,
      {
        responseType: "blob",
        params: {
          digest: digest,
        },
      },
    );
    return new Blob([resp.data]);
  }
  async askQuestion(contestName: string, data: QuestionParams): Promise<void> {
    await http.post(
      `/api/cms/contest/${encodeURIComponent(contestName)}/question`,
      data,
    );
  }
  async askQuestionTask(
    contestName: string,
    taskName: string,
    data: QuestionParams,
  ): Promise<void> {
    await http.post(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/question`,
      data,
    );
  }
  async submit(
    contestName: string,
    taskName: string,
    data: SubmitParams,
  ): Promise<SubmitResult> {
    const resp = await http.post(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/submit`,
      data,
    );
    return resp.data;
  }
  async userEval(
    contestName: string,
    taskName: string,
    data: UserEvalSubmitParams,
  ): Promise<UserEvalSubmitResult> {
    const resp = await http.post(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/eval`,
      data,
    );
    return resp.data;
  }
  async getUserEval(
    contestName: string,
    taskName: string,
    userEvalUuid: string,
  ): Promise<UserEval> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(
        contestName,
      )}/task/${encodeURIComponent(taskName)}/user-eval/${encodeURIComponent(
        userEvalUuid,
      )}`,
    );
    return resp.data;
  }
  async checkNotifications(
    contestName: string,
    data: CheckNotificationsParams,
  ): Promise<CheckNotificationsResult> {
    const resp = await http.post(
      `/api/cms/contest/${encodeURIComponent(contestName)}/check-notifications`,
      data,
    );
    return resp.data;
  }
  async getContestScores(contestName: string): Promise<ContestTaskScores> {
    const resp = await http.get(
      `/api/cms/contest/${encodeURIComponent(contestName)}/scores`,
    );
    return resp.data;
  }
}
export default new CMSService();
