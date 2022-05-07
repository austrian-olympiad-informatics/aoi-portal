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
import ErrorView from "../views/ErrorView.vue";
import store from "@/store";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/error",
    name: "Error",
    component: ErrorView,
    meta: {
      requiresAuth: false,
      noNavAuth: true
    }
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
        path: "settings",
        name: "AdminSettings",
        component: () =>
          import(
            /* webpackChunkName: "admin" */ "../views/admin/SettingsView.vue"
          ),
      },
    ],
  },
  {
    path: "/contests/:contestUuid/sso",
    name: "ContestSSO",
    component: ContestSSOView,
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
