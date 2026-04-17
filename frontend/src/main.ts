import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import Buefy from "buefy";
import VueMatomo from "vue-matomo";
import { pinia } from "./store";
import { initApiClient } from "./services/common";
import { initNotification } from "./util/errors";
import "@/scss/style.scss";
import AOIIconPack from "./components/AOIIconPack.vue";

const app = createApp(App);

app.component("aoi-icon-pack", AOIIconPack);

app.use(Buefy, {
  defaultIconComponent: "aoi-icon-pack",
  defaultIconPack: "aoi",
  customIconPacks: {
    aoi: {
      sizes: {
        default: "24px",
        "is-small": "16px",
        "is-medium": "36px",
        "is-large": "48px",
      },
      iconPrefix: "",
    },
  },
});

app.use(pinia);
initApiClient();
initNotification(app);
app.use(router);

if (process.env.NODE_ENV === "production") {
  app.use(VueMatomo, {
    host: "https://matomo.informatikolympiade.at",
    siteId: 2,
    router: router,
    disableCookies: true,
  });
}

app.mount("#app");
