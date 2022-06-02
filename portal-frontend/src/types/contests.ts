export interface Contest {
  uuid: string;
  name: string;
  teaser: string;
  description: string;
  joined: boolean;
  open_signup: boolean;
  quali_round: boolean;
  order_priority: number;
  archived: boolean;
  url?: string;
  sso_enabled?: boolean;
  cms_name?: string;
  allow_frontendv2?: boolean;
}

export type Contests = Contest[];

export type ContestDetail = Omit<Contest, "uuid">;

export interface GenSSOTokenResponse {
  endpoint: string;
  token: string;
}
