import {
  NewsletterSignupParams,
  NewsletterUnsubscribeParams,
} from "@/types/newsletter";
import http from "./common";

class NewsletterService {
  async signUp(params: NewsletterSignupParams): Promise<void> {
    await http.post("/api/newsletter/signup", params);
  }
  async unsubscribe(params: NewsletterUnsubscribeParams): Promise<void> {
    await http.post("/api/newsletter/unsubscribe", params);
  }
}
export default new NewsletterService();
