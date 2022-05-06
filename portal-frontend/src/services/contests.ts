import http from "./common";
import { Contests, GenSSOTokenResponse } from "@/types/contests";

class ContestsService {
  async listContests(): Promise<Contests> {
    const resp = await http.get("/api/contests");
    return resp.data;
  }
  async joinContest(contestUuid: string): Promise<void> {
    await http.post(`/api/contests/${encodeURIComponent(contestUuid)}/join`);
  }
  async genSSOToken(contestUuid: string): Promise<GenSSOTokenResponse> {
    const resp = await http.post(
      `/api/contests/${encodeURIComponent(contestUuid)}/gen-sso-token`
    );
    return resp.data;
  }
}
export default new ContestsService();
