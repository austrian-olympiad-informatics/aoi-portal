export interface AuthLoginParams {
  email: string;
  password: string;
}
export interface AuthLoginResult {
  token: string;
}
export interface AuthStatusResult {
  authenticated: boolean;
  admin: boolean;
  first_name?: string;
  last_name?: string;
  discord_user?: string;
}
export interface AuthRegisterParams {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
}
export interface AuthRegisterResult {
  uuid: string;
}
export interface AuthRegisterVerifyParams {
  uuid: string;
  verification_code: string;
}
export interface AuthRegisterVerifyResult {
  token: string;
}

export interface AuthChangePasswordParams {
  old_password?: string;
  new_password: string;
}
export interface AuthRequestPasswordResetParams {
  email: string;
}
export interface AuthRequestPasswordResetResult {
  uuid: string;
}
export interface AuthResetPasswordParams {
  uuid: string;
  verification_code: string;
  new_password?: string;
}
export interface AuthResetPasswordResult {
  token: string;
}
export interface AuthChangeEmailParams {
  password?: string;
  email: string;
}
export interface AuthChangeEmailResult {
  uuid: string;
}
export interface AuthChangeEmailVerifyParams {
  uuid: string;
  verification_code: string;
}
