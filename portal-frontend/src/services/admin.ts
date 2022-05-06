import http from "./common";
import {
  AdminContestCreateParticipationParams,
  AdminContestDetail,
  AdminContestImportGroupParams,
  AdminContestParticipation,
  AdminContestParticipationUpdateParams,
  AdminContests,
  AdminContestUpdateParams,
  AdminGroupCreateParams,
  AdminGroupDetail,
  AdminGroups,
  AdminGroupUpdateParams,
  AdminUserCreateParams,
  AdminUserDetail,
  AdminUsers,
  AdminUserUpdateParams,
} from "@/types/admin";

class AdminService {
  async getUsers(): Promise<AdminUsers> {
    const resp = await http.get("/api/admin/users");
    return resp.data;
  }
  async getUser(userId: number): Promise<AdminUserDetail> {
    const resp = await http.get(
      `/api/admin/users/${encodeURIComponent(userId)}`
    );
    return resp.data;
  }
  async deleteUser(userId: number): Promise<void> {
    await http.delete(`/api/admin/users/${encodeURIComponent(userId)}/delete`);
  }
  async updateUser(
    userId: number,
    params: AdminUserUpdateParams
  ): Promise<void> {
    await http.put(
      `/api/admin/users/${encodeURIComponent(userId)}/update`,
      params
    );
  }
  async createUser(params: AdminUserCreateParams): Promise<void> {
    await http.post("/api/admin/users/create", params);
  }
  async refreshCMSContests(): Promise<void> {
    await http.post("/api/admin/refresh-cms-contests");
  }
  async getContests(): Promise<AdminContests> {
    const resp = await http.get("/api/admin/contests");
    return resp.data;
  }
  async getContest(contestUuid: string): Promise<AdminContestDetail> {
    const resp = await http.get(
      `/api/admin/contests/${encodeURIComponent(contestUuid)}`
    );
    return resp.data;
  }
  async updateContest(
    contestUuid: string,
    params: AdminContestUpdateParams
  ): Promise<void> {
    await http.put(
      `/api/admin/contests/${encodeURIComponent(contestUuid)}/update`,
      params
    );
  }
  async contestProvisionSSO(contestUuid: string): Promise<void> {
    await http.post(
      `/api/admin/contests/${encodeURIComponent(contestUuid)}/provision-sso`
    );
  }
  async contestRemoveSSO(contestUuid: string): Promise<void> {
    await http.post(
      `/api/admin/contests/${encodeURIComponent(contestUuid)}/remove-sso`
    );
  }
  async createContestParticipation(
    contestUuid: string,
    params: AdminContestCreateParticipationParams
  ): Promise<number> {
    const resp = await http.post(
      `/api/admin/contests/${encodeURIComponent(
        contestUuid
      )}/participations/create`,
      params
    );
    return resp.data.id;
  }
  async getContestParticipation(
    contestUuid: string,
    participationId: number
  ): Promise<AdminContestParticipation> {
    const resp = await http.get(
      `/api/admin/contests/${encodeURIComponent(
        contestUuid
      )}/participations/${encodeURIComponent(participationId)}`
    );
    return resp.data;
  }
  async updateContestParticipation(
    contestUuid: string,
    participationId: number,
    params: AdminContestParticipationUpdateParams
  ): Promise<void> {
    await http.put(
      `/api/admin/contests/${encodeURIComponent(
        contestUuid
      )}/participations/${encodeURIComponent(participationId)}/update`,
      params
    );
  }
  async deleteContestParticipation(
    contestUuid: string,
    participationId: number
  ): Promise<void> {
    await http.delete(
      `/api/admin/contests/${encodeURIComponent(
        contestUuid
      )}/participations/${encodeURIComponent(participationId)}/delete`
    );
  }
  async contestImportGroup(
    contestUuid: string,
    params: AdminContestImportGroupParams
  ): Promise<void> {
    await http.post(
      `/api/admin/contests/${encodeURIComponent(contestUuid)}/import-group`,
      params
    );
  }
  async getGroups(): Promise<AdminGroups> {
    const resp = await http.get("/api/admin/groups");
    return resp.data;
  }
  async getGroup(groupId: number): Promise<AdminGroupDetail> {
    const resp = await http.get(
      `/api/admin/groups/${encodeURIComponent(groupId)}`
    );
    return resp.data;
  }
  async updateGroup(
    groupId: number,
    params: AdminGroupUpdateParams
  ): Promise<void> {
    await http.put(`/api/admin/groups/${encodeURIComponent(groupId)}/update`, params);
  }
  async createGroup(params: AdminGroupCreateParams): Promise<number> {
    const resp = await http.post("/api/admin/groups/create", params);
    return resp.data.id;
  }
  async deleteGroup(groupId: number): Promise<void> {
    await http.delete(
      `/api/admin/groups/${encodeURIComponent(groupId)}/delete`
    );
  }
}
export default new AdminService();
