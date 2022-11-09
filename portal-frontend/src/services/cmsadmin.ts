import {
  AdminAllTasks,
  AdminAnnouncements,
  AdminContest,
  AdminContestParticipations,
  AdminContests,
  AdminContestTasks,
  AdminMeme,
  AdminMemes,
  AdminMessage,
  AdminParticipation,
  AdminQuestion,
  AdminSubmissionDetailed,
  AdminSubmissionsPaginated,
  AdminTaskDetailed,
  AdminUser,
  AdminUserEvalDetailed,
  AdminUserEvalsPaginated,
  AdminUsers,
} from "@/types/cmsadmin";
import http from "./common";

class CMSAdminService {
  async getContests(): Promise<AdminContests> {
    const resp = await http.get("/api/cms/admin/contests");
    return resp.data;
  }
  async getContest(contestId: number): Promise<AdminContest> {
    const resp = await http.get(
      `/api/cms/admin/contest/${encodeURIComponent(contestId)}`
    );
    return resp.data;
  }
  async getContestAnnouncements(
    contestId: number
  ): Promise<AdminAnnouncements> {
    const resp = await http.get(
      `/api/cms/admin/contest/${encodeURIComponent(contestId)}/announcements`
    );
    return resp.data;
  }
  async getContestQuestions(
    contestId: number
  ): Promise<AdminQuestion> {
    const resp = await http.get(
      `/api/cms/admin/contest/${encodeURIComponent(contestId)}/questions`
    );
    return resp.data;
  }
  async getContestMessages(
    contestId: number
  ): Promise<AdminMessage> {
    const resp = await http.get(
      `/api/cms/admin/contest/${encodeURIComponent(contestId)}/messages`
    );
    return resp.data;
  }
  async getContestTasks(
    contestId: number
  ): Promise<AdminContestTasks> {
    const resp = await http.get(
      `/api/cms/admin/contest/${encodeURIComponent(contestId)}/tasks`
    );
    return resp.data;
  }
  async getContestParticipations(
    contestId: number
  ): Promise<AdminContestParticipations> {
    const resp = await http.get(
      `/api/cms/admin/contest/${encodeURIComponent(contestId)}/participations`
    );
    return resp.data;
  }
  async getParticipation(
    participationId: number
  ): Promise<AdminParticipation> {
    const resp = await http.get(
      `/api/cms/admin/participation/${encodeURIComponent(participationId)}`
    );
    return resp.data;
  }
  async getParticipationQuestions(
    participationId: number
  ): Promise<AdminQuestion[]> {
    const resp = await http.get(
      `/api/cms/admin/participation/${encodeURIComponent(participationId)}/questions`
    );
    return resp.data;
  }
  async getParticipationMessages(
    participationId: number
  ): Promise<AdminMessage[]> {
    const resp = await http.get(
      `/api/cms/admin/participation/${encodeURIComponent(participationId)}/messages`
    );
    return resp.data;
  }
  async getSubmissions(
    args?: {
      contestId?: number;
      taskId?: number;
      userId?: number;
      perPage?: number;
      page?: number;
    }
  ): Promise<AdminSubmissionsPaginated> {
    const resp = await http.get("/api/cms/admin/submissions", {
      params: {
        contest_id: args?.contestId,
        task_id: args?.taskId,
        user_id: args?.userId,
        per_page: args?.perPage,
        page: args?.page,
      }
    });
    return resp.data;
  }
  async getUserEvals(
    args?: {
      contestId?: number;
      taskId?: number;
      userId?: number;
      perPage?: number;
      page?: number;
    }
  ): Promise<AdminUserEvalsPaginated> {
    const resp = await http.get("/api/cms/admin/user-evals", {
      params: {
        contest_id: args?.contestId,
        task_id: args?.taskId,
        user_id: args?.userId,
        per_page: args?.perPage,
        page: args?.page,
      }
    });
    return resp.data;
  }
  async getSubmission(
    submissionUuid: string
  ): Promise<AdminSubmissionDetailed> {
    const resp = await http.get(
      `/api/cms/admin/submission/${encodeURIComponent(submissionUuid)}`
    );
    return resp.data;
  }
  async getUserEval(
    userEvalUuid: string
  ): Promise<AdminUserEvalDetailed> {
    const resp = await http.get(
      `/api/cms/admin/user-eval/${encodeURIComponent(userEvalUuid)}`
    );
    return resp.data;
  }
  async getDigest(digest: string): Promise<Blob> {
    const resp = await http.get(
      `/api/cms/admin/digest/${encodeURIComponent(digest)}`,
      {
        responseType: "blob",
      }
    );
    return new Blob([resp.data]);
  }
  async getTasks(): Promise<AdminAllTasks> {
    const resp = await http.get("/api/cms/admin/tasks");
    return resp.data;
  }
  async getUsers(): Promise<AdminUsers> {
    const resp = await http.get("/api/cms/admin/users");
    return resp.data;
  }
  async getMemes(): Promise<AdminMemes> {
    const resp = await http.get("/api/cms/admin/memes");
    return resp.data;
  }
  async getMeme(id: number): Promise<AdminMeme> {
    const resp = await http.get(`/api/cms/admin/meme/${encodeURIComponent(id)}`);
    return resp.data;
  }
  async getTask(id: number): Promise<AdminTaskDetailed> {
    const resp = await http.get(`/api/cms/admin/task/${encodeURIComponent(id)}`);
    return resp.data;
  }
  async getUser(id: number): Promise<AdminUser> {
    const resp = await http.get(`/api/cms/admin/user/${encodeURIComponent(id)}`);
    return resp.data;
  }
}
export default new CMSAdminService();
