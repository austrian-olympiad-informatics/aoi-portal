import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginView from "../views/auth/LoginView.vue";
import RegisterView from "../views/auth/RegisterView.vue";
import RegisterVerifyView from "../views/auth/RegisterVerifyView.vue";
import ContestSSOView from "../views/ContestSSOView.vue";
import ProfileView from "../views/ProfileView.vue";
import ChangePasswordView from "../views/auth/ChangePasswordView.vue";
import ChangeEmailView from "../views/auth/ChangeEmailView.vue";
import ChangeEmailVerifyView from "../views/auth/ChangeEmailVerifyView.vue";
import PasswordResetView from "../views/auth/PasswordResetView.vue";
import PasswordResetVerifyView from "../views/auth/PasswordResetVerifyView.vue";
import GitHubOAuthView from "../views/auth/GitHubOAuthView.vue";
import GitHubOAuthCallbackView from "../views/auth/GitHubOAuthCallbackView.vue";
import GoogleOAuthView from "../views/auth/GoogleOAuthView.vue";
import GoogleOAuthCallbackView from "../views/auth/GoogleOAuthCallbackView.vue";
import DiscordOAuthView from "../views/auth/DiscordOAuthView.vue";
import DiscordOAuthCallbackView from "../views/auth/DiscordOAuthCallbackView.vue";
import ErrorView from "../views/ErrorView.vue";
import ContestView from "../views/ContestView.vue";
import NewsletterSignUpView from "../views/NewsletterSignUpView.vue";
import NewsletterUnsubscribeView from "../views/NewsletterUnsubscribeView.vue";
import store from "@/store";

Vue.use(VueRouter);

const CMS_META = {
  navbarSmall: true,
  footerHidden: true,
  isCMS: true,
};

const routes: Array<RouteConfig> = [
  {
    path: "/error",
    name: "Error",
    component: ErrorView,
    meta: {
      requiresAuth: false,
      noNavAuth: true,
    },
  },
  {
    path: "/",
    name: "Home",
    component: HomeView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/auth/login",
    name: "Login",
    component: LoginView,
    meta: {
      requiresAuth: false,
      noNavAuth: true,
    },
  },
  {
    path: "/auth/register",
    name: "Register",
    component: RegisterView,
    meta: {
      requiresAuth: false,
      noNavAuth: true,
    },
  },
  {
    path: "/auth/register-verify",
    name: "RegisterVerify",
    component: RegisterVerifyView,
    meta: {
      requiresAuth: false,
      noNavAuth: true,
    },
  },
  {
    path: "/profile",
    name: "Profile",
    component: ProfileView,
  },
  {
    path: "/auth/change-password",
    name: "ChangePassword",
    component: ChangePasswordView,
  },
  {
    path: "/auth/change-email",
    name: "ChangeEmail",
    component: ChangeEmailView,
  },
  {
    path: "/auth/change-verify-email",
    name: "ChangeEmailVerify",
    component: ChangeEmailVerifyView,
  },
  {
    path: "/auth/password-reset",
    name: "PasswordReset",
    component: PasswordResetView,
    meta: {
      requiresAuth: false,
      noNavAuth: true,
    },
  },
  {
    path: "/auth/password-reset-verify",
    name: "PasswordResetVerify",
    component: PasswordResetVerifyView,
    meta: {
      requiresAuth: false,
      noNavAuth: true,
    },
  },
  {
    path: "/auth/oauth/github/authorize",
    name: "GitHubOAuth",
    component: GitHubOAuthView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/auth/oauth/github/callback",
    name: "GitHubOAuthCallback",
    component: GitHubOAuthCallbackView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/auth/oauth/google/authorize",
    name: "GoogleOAuth",
    component: GoogleOAuthView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/auth/oauth/google/callback",
    name: "GoogleOAuthCallback",
    component: GoogleOAuthCallbackView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/auth/oauth/discord/authorize",
    name: "DiscordOAuth",
    component: DiscordOAuthView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/auth/oauth/discord/callback",
    name: "DiscordOAuthCallback",
    component: DiscordOAuthCallbackView,
    meta: {
      requiresAuth: true,
    }
  },
  {
    path: "/newsletter/sign-up",
    name: "NewsletterSignUp",
    component: NewsletterSignUpView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/newsletter/unsubscribe",
    name: "NewsletterUnsubscribe",
    component: NewsletterUnsubscribeView,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: "/admin",
    name: "AdminIndex",
    component: () =>
      import(/* webpackChunkName: "admin" */ "../views/admin/IndexView.vue"),
    meta: {
      requiresAdmin: true,
    },
    children: [
      {
        path: "users",
        name: "AdminUsers",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/UsersView.vue"
          ),
      },
      {
        path: "users/create",
        name: "AdminUserCreate",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/UserCreateView.vue"
          ),
      },
      {
        path: "users/:userId",
        name: "AdminUser",
        component: () =>
          import(/* webpackChunkName: "admin" */ "../views/admin/UserView.vue"),
      },
      {
        path: "contests",
        name: "AdminContests",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/ContestsView.vue"
          ),
      },
      {
        path: "contests/:contestUuid",
        name: "AdminContest",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/ContestView.vue"
          ),
      },
      {
        path: "groups",
        name: "AdminGroups",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/GroupsView.vue"
          ),
      },
      {
        path: "groups/create",
        name: "AdminGroupCreate",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/GroupCreateView.vue"
          ),
      },
      {
        path: "groups/:groupId",
        name: "AdminGroup",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/GroupView.vue"
          ),
      },
      {
        path: "user-mail",
        name: "AdminUserMail",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/UserMailView.vue"
          ),
      },
      {
        path: "newsletter",
        name: "AdminNewsletter",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/NewsletterView.vue"
          ),
      },
      {
        path: "newsletter/mail",
        name: "AdminNewsletterMail",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/NewsletterMailView.vue"
          ),
      },
    ],
  },
  {
    path: "/contests/:contestUuid/sso",
    name: "ContestSSO",
    component: ContestSSOView,
  },
  {
    path: "/contests/:contestUuid",
    name: "Contest",
    component: ContestView,
  },
  {
    path: "/cms/contest/:contestName",
    name: "CMSContest",
    component: () =>
      import(/* webpackChunkName: "cms" */ "../views/cms/ContestView.vue"),
    meta: CMS_META,
  },
  {
    path: "/cms/contest/:contestName/task/:taskName",
    component: () =>
      import(/* webpackChunkName: "cms" */ "../views/cms/TaskView.vue"),
    meta: {
      ...CMS_META,
      isAdminButtonHidden: true,
    },
    children: [
      {
        path: "",
        name: "CMSTask",
        component: () =>
          import(/* webpackChunkName: "cms" */ "../views/cms/CodePanel.vue"),
      },
      {
        path: "submission/:submissionUuid",
        name: "CMSSubmissionDetails",
        component: () =>
          import(
            /* webpackChunkName: "cms" */ "../views/cms/SubmissionDetailsPanel.vue"
          ),
      },
    ],
  },
  {
    path: "/cms/admin/submissions",
    name: "CMSAdminSubmissions",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/SubmissionsView.vue"),
    meta: CMS_META,
    children: [
      {
        path: "submission/:submissionUuid",
        name: "CMSAdminSubmission",
        component: () =>
          import(
            /* webpackChunkName: "cmsadmin" */ "../views/cms/admin/SubDetailsPanel.vue"
          ),
      }
    ]
  },
  {
    path: "/cms/admin/user-evals",
    name: "CMSAdminUserEvals",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/UserEvalsView.vue"),
    meta: CMS_META,
    children: [
      {
        path: "user-eval/:userEvalUuid",
        name: "CMSAdminUserEval",
        component: () =>
          import(
            /* webpackChunkName: "cmsadmin" */ "../views/cms/admin/UserEvalDetailsPanel.vue"
          ),
      }
    ]
  },
  {
    path: "/cms/admin",
    name: "CMSAdminIndex",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/IndexView.vue"),
    meta: CMS_META,
  },
  {
    path: "/cms/admin/contest/:contestId",
    name: "CMSAdminContest",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/ContestView.vue"),
    meta: CMS_META,
  },
  {
    path: "/cms/admin/validity-helper/:contestId",
    name: "CMSAdminValidityHelper",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/ValidityHelperView.vue"),
    meta: CMS_META,
  },
  {
    path: "/cms/admin/task/:taskId",
    name: "CMSAdminTask",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/TaskView.vue"),
    meta: CMS_META,
  },
  {
    path: "/cms/admin/user/:userId",
    name: "CMSAdminUser",
    component: () =>
      import(/* webpackChunkName: "cmsadmin" */ "../views/cms/admin/UserView.vue"),
    meta: CMS_META,
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

// Ensure store initialized before any routing happens
// https://stackoverflow.com/a/51495462
const storeInit = store.dispatch("init");

// check requires auth
router.beforeEach((to, from, next) => {
  if (to.matched.every((r) => r.meta.requiresAuth === false)) {
    next();
    return;
  }
  storeInit.then(() => {
    if (!store.getters.isAuthenticated) {
      next("/auth/login");
      return;
    }
    next();
  });
});

// check requires admin
router.beforeEach((to, from, next) => {
  if (to.matched.some((r) => r.meta.requiresAdmin)) {
    storeInit.then(() => {
      if (!store.getters.isAuthenticated) {
        next("/auth/login");
        return;
      }
      next();
    });
    return;
  }
  next();
});

export default router;
