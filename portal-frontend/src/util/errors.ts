import { AxiosError } from "axios";
import { NotificationProgrammatic as Notification } from "buefy";

type ErrorCode =
  | "already_logged_in"
  | "login_required"
  | "admin_required"
  | "validation_error"
  | "user_not_found"
  | "invalid_password"
  | "email_exists"
  | "rate_limit"
  | "no_longer_valid"
  | "too_many_attempts"
  | "invalid_verification_code";

type Handlers = {
  [key in ErrorCode | "default"]?: string | (() => void);
};
interface ErrorResponse {
  error: boolean;
  message: string;
  error_code: string;
}

export const matchError = (err: unknown, handlers: Handlers) => {
  if (!(err instanceof AxiosError)) {
    if (!callHandler(handlers.default)) throw err;
    return;
  }

  if (!err.response) {
    if (!callHandler(handlers.default)) throw err;
    return;
  }
  const rawData = err.response.data;

  if (!Object.prototype.hasOwnProperty.call(rawData, "error")) {
    if (!callHandler(handlers.default)) throw err;
    return;
  }

  const data = rawData as ErrorResponse;
  for (const [k, v] of Object.entries(handlers)) {
    if (k === data.error_code) {
      if (callHandler(v)) return;
    }
  }

  if (!callHandler(handlers.default)) throw err;
};

export const callHandler = (handler: string | (() => void) | undefined) => {
  if (handler !== undefined) {
    if (typeof handler === "string") showErrorNotification(handler);
    else handler();
    return true;
  }

  return false;
};

export const showErrorNotification = (message: string) => {
  Notification.open({
    message: message,
    type: "is-danger",
    hasIcon: true,
    position: "is-top-right",
    duration: 5000,
  });
};
