export interface Contest {
  uuid: string;
  name: string;
  description: string;
  joined: boolean;
  can_join: boolean;
  url?: string;
  sso_enabled?: boolean;
}

export type Contests = Contest[];

export interface GenSSOTokenResponse {
  endpoint: string;
  token: string;
}
