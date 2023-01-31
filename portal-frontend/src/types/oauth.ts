import exp from "constants";

export interface GitHubAuthorizeURLResponse {
  url: string;
}

export interface GitHubAuthorizeParams {
  code: string;
}

export interface GitHubAuthorizeResponse {
  token: string;
}

export interface DiscordAuthorizeURLResponse {
  url: string;
}

export interface DiscordAuthorizeParams {
  code: string;
  redirect_uri: string;
}

export interface DiscordAuthorizeResponse {
  user_id: string;
  username: string;
}

export interface GoogleAuthorizeURLResponse {
  url: string;
}

export interface GoogleAuthorizeParams {
  code: string;
  redirect_uri: string;
}

export interface GoogleAuthorizeResponse {
  token: string;
}
