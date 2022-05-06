export interface AdminUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  created_at: string | null;
  last_login: string | null;
  is_admin: boolean;
  birthday: string | null;
  phone_nr: string | null;
  address_street: string | null;
  address_zip: string | null;
  address_town: string | null;
  school_name: string | null;
  school_address: string | null;
  cms_id: number | null;
  cms_username: string | null;
  groups: {
    id: number;
    name: string;
  };
}

export type AdminUsers = AdminUser[];

export interface AdminUserDetail extends Omit<AdminUser, "groups"> {
  groups: {
    id: number;
    name: string;
    description: string;
  }[];
  participations: {
    id: number;
    contest: {
      uuid: string;
      cms_name: string;
      cms_description: string;
    };
  }[];
}

export interface AdminUserUpdateParams {
  first_name?: string;
  last_name?: string;
  email?: string;
  password?: string;
  is_admin?: boolean;
  birthday?: string | null;
  phone_nr?: string | null;
  address_street?: string | null;
  address_zip?: string | null;
  address_town?: string | null;
  school_name?: string | null;
  school_address?: string | null;
  cms_id?: number | null;
  cms_username?: string | null;
  groups?: number[];
}

export interface AdminUserCreateParams {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  is_admin?: boolean;
  birthday?: string | null;
  phone_nr?: string | null;
  address_street?: string | null;
  address_zip?: string | null;
  address_town?: string | null;
  school_name?: string | null;
  school_address?: string | null;
  cms_id?: number | null;
  cms_username?: string | null;
  groups?: number[];
}

export interface AdminContest {
  uuid: string;
  cms_id: number;
  cms_name: string;
  cms_description: string;
  cms_allow_sso_authentication: boolean;
  cms_sso_redirect_url: string;
  url: string;
  public: boolean;
  auto_add_to_group: null | {
    id: number;
    name: string;
    description: string;
  };
  participant_count: number;
}

export type AdminContests = AdminContest[];

export interface AdminContestDetail
  extends Omit<AdminContest, "participation_count"> {
  cms_sso_secret_key: string;
  cms_sso_redirect_url: string;
  participations: {
    id: number;
    cms_id: number;
    user: {
      id: number;
      first_name: string;
      last_name: string;
      username: string;
    };
    manual_password: string;
  }[];
}

export interface AdminContestUpdateParams {
  public?: boolean;
  auto_add_to_group_id?: number | null;
  url?: string;
}

export interface AdminContestCreateParticipationParams {
  user_id: number;
  cms_id?: number | null;
  manual_password?: string | null;
}

export interface AdminContestParticipation {
  cms_id: number;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    cms_username: string;
  };
  manual_password: string;
}

export interface AdminContestParticipationUpdateParams {
  cms_id?: number;
  manual_password?: string | null;
}

export interface AdminContestImportGroupParams {
  group_id: number;
  random_manual_passwords?: boolean;
}

export interface AdminGroup {
  id: number;
  name: string;
  description: string;
  user_count: number;
}

export type AdminGroups = AdminGroup[];

export interface AdminGroupDetail extends Omit<AdminGroup, "user_count"> {
  users: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  }[];
}

export interface AdminGroupUpdateParams {
  name?: string;
  description?: string;
  users?: number[];
}

export interface AdminGroupCreateParams {
  name: string;
  description: string;
  users?: number[];
}
