export interface AuthLoginParams {
  email: string;
  password: string;
}
export interface AuthStatusResult {
  authenticated: boolean;
  admin: boolean;
}
export interface AuthRegisterParams {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
}
export interface AuthRequestVerificationCodeParams {
  email: string;
}
export interface AuthVerifyEmailParams {
  email: string;
}
export interface AuthVerifyEmailParams {
  token: string;
}
export interface AuthChangePasswordParams {
  old_password?: string;
  new_password: string;
}
export interface AuthRequestPasswordResetParams {
  email: string;
}
export interface AuthResetPasswordParams {
  token: string;
  password: string;
}
export interface AuthChangeEmailParams {
  password?: string;
  email: string;
}
