import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import Buefy from "buefy";
import VueMatomo from "vue-matomo";
import store from "./store";
import "@/scss/style.scss";
import AOIIconPack from "./components/AOIIconPack.vue";

Vue.component("aoi-icon-pack", AOIIconPack);

Vue.use(Buefy, {
  defaultIconComponent: "aoi-icon-pack",
  defaultIconPack: "aoi",
  customIconPacks: {
    aoi: {
      sizes: {
        'default': '24px',
        'is-small': "16px",
        'is-medium': '36px',
        'is-large': '48px',
      },
      iconPrefix: "",
    },
  },
});
Vue.config.productionTip = false;

if (process.env.NODE_ENV === 'production') {
  Vue.use(VueMatomo, {
    host: 'https://matomo.informatikolympiade.at',
    siteId: 2,
    router: router,
    disableCookies: true,
  });
}

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
