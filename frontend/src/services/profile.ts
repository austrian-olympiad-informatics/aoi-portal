import http from "./common";
import { ProfileInfoResponse, ProfileUpdateParams } from "@/types/profile";

class ProfileService {
  async profileInfo(): Promise<ProfileInfoResponse> {
    const resp = await http.get("/api/profile/info");
    return resp.data;
  }
  async updateProfile(params: ProfileUpdateParams): Promise<void> {
    await http.put("/api/profile/update", params);
  }
}
export default new ProfileService();
