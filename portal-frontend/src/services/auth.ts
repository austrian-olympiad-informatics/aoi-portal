import http from "./common";
import {AuthChangeEmailParams, AuthChangePasswordParams, AuthLoginParams, AuthRegisterParams, AuthRequestPasswordResetParams, AuthRequestVerificationCodeParams, AuthResetPasswordParams, AuthStatusResult, AuthVerifyEmailParams} from "@/types/auth";

class AuthService {
  async login(params: AuthLoginParams): Promise<void> {
    await http.post("/api/auth/login", params);
  }
  async status(): Promise<AuthStatusResult> {
    return await http.get("/api/auth/status");
  }
  async logout(): Promise<void> {
    return await http.post("/api/auth/logout");
  }
  async register(params: AuthRegisterParams): Promise<void> {
    await http.post("/api/auth/register", params);
  }
  async requestVerificationCode(
    params: AuthRequestVerificationCodeParams
  ): Promise<void> {
    await http.post("/api/auth/request-verification-code", params);
  }
  async verifyEmail(params: AuthVerifyEmailParams): Promise<void> {
    await http.post("/api/auth/verify-email", params);
  }
  async changePassword(params: AuthChangePasswordParams): Promise<void> {
    await http.post("/api/auth/change-password", params);
  }
  async requestPasswordReset(params: AuthRequestPasswordResetParams): Promise<void> {
    await http.post("/api/auth/request-password-reset", params);
  }
  async resetPassword(params: AuthResetPasswordParams): Promise<void> {
    await http.post("/api/auth/reset-password", params);
  }
  async changeEmail(params: AuthChangeEmailParams): Promise<void> {
    await http.post("/api/auth/change-email", params);
  }
}
export default new AuthService();
