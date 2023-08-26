import http from "./common";
import { ContestDetail, Contests, GenSSOTokenResponse } from "@/types/contests";

class ContestsService {
  async listContests(): Promise<Contests> {
    const resp = await http.get("/api/contests");
    return resp.data;
  }
  async getContest(contestUuid: string): Promise<ContestDetail> {
    const resp = await http.get(
      `/api/contests/${encodeURIComponent(contestUuid)}`,
    );
    return resp.data;
  }
  async joinContest(contestUuid: string): Promise<void> {
    await http.post(`/api/contests/${encodeURIComponent(contestUuid)}/join`);
  }
  async genSSOToken(contestUuid: string): Promise<GenSSOTokenResponse> {
    const resp = await http.post(
      `/api/contests/${encodeURIComponent(contestUuid)}/gen-sso-token`,
    );
    return resp.data;
  }
}
export default new ContestsService();
