import http from "./common";
import {
  GitHubAuthorizeParams,
  GitHubAuthorizeResponse,
  GitHubAuthorizeURLResponse,
  GoogleAuthorizeParams,
  GoogleAuthorizeResponse,
  GoogleAuthorizeURLResponse,
  DiscordAuthorizeParams,
  DiscordAuthorizeResponse,
  DiscordAuthorizeURLResponse,
} from "@/types/oauth";

class OAuthService {
  async getGithubAuthorizeURL(): Promise<GitHubAuthorizeURLResponse> {
    const resp = await http.get("/api/auth/oauth/github/authorize-url");
    return resp.data;
  }
  async githubAuthorize(
    data: GitHubAuthorizeParams,
  ): Promise<GitHubAuthorizeResponse> {
    const resp = await http.post("/api/oauth/github/auth", data);
    return resp.data;
  }
  async getGoogleAuthorizeURL(): Promise<GoogleAuthorizeURLResponse> {
    const resp = await http.get("/api/auth/oauth/google/authorize-url");
    return resp.data;
  }
  async googleAuthorize(
    data: GoogleAuthorizeParams,
  ): Promise<GoogleAuthorizeResponse> {
    const resp = await http.post("/api/oauth/google/auth", data);
    return resp.data;
  }
  async getDiscordAuthorizeURL(): Promise<DiscordAuthorizeURLResponse> {
    const resp = await http.get("/api/auth/oauth/discord/authorize-url");
    return resp.data;
  }
  async discordAuthorize(
    data: DiscordAuthorizeParams,
  ): Promise<DiscordAuthorizeResponse> {
    const resp = await http.post("/api/oauth/discord/auth", data);
    return resp.data;
  }
}
export default new OAuthService();
