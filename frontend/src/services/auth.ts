import http from "./common";
import {
  AuthChangeEmailParams,
  AuthChangeEmailResult,
  AuthChangeEmailVerifyParams,
  AuthChangePasswordParams,
  AuthLoginParams,
  AuthLoginResult,
  AuthRegisterParams,
  AuthRegisterResult,
  AuthRegisterVerifyParams,
  AuthRegisterVerifyResult,
  AuthRequestPasswordResetParams,
  AuthRequestPasswordResetResult,
  AuthResetPasswordParams,
  AuthResetPasswordResult,
  AuthStatusResult,
} from "@/types/auth";

class AuthService {
  async login(params: AuthLoginParams): Promise<AuthLoginResult> {
    const resp = await http.post("/api/auth/login", params);
    return resp.data;
  }
  async status(): Promise<AuthStatusResult> {
    const resp = await http.get("/api/auth/status");
    return resp.data;
  }
  async logout(): Promise<void> {
    await http.post("/api/auth/logout");
  }
  async register(params: AuthRegisterParams): Promise<AuthRegisterResult> {
    const resp = await http.post("/api/auth/register", params);
    return resp.data;
  }
  async registerVerify(
    params: AuthRegisterVerifyParams
  ): Promise<AuthRegisterVerifyResult> {
    const resp = await http.post("/api/auth/register-verify", params);
    return resp.data;
  }
  async changePassword(params: AuthChangePasswordParams): Promise<void> {
    await http.post("/api/auth/change-password", params);
  }
  async requestPasswordReset(
    params: AuthRequestPasswordResetParams
  ): Promise<AuthRequestPasswordResetResult> {
    const resp = await http.post("/api/auth/request-password-reset", params);
    return resp.data;
  }
  async resetPassword(
    params: AuthResetPasswordParams
  ): Promise<AuthResetPasswordResult> {
    const resp = await http.post("/api/auth/reset-password", params);
    return resp.data;
  }
  async changeEmail(
    params: AuthChangeEmailParams
  ): Promise<AuthChangeEmailResult> {
    const resp = await http.post("/api/auth/change-email", params);
    return resp.data;
  }
  async changeEmailVerify(params: AuthChangeEmailVerifyParams): Promise<void> {
    await http.post("/api/auth/change-email-verify", params);
  }
}
export default new AuthService();
