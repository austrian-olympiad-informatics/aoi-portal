import Vue from "vue";
import Notfifications from "vue-notification"
import App from "./App.vue";
import router from "./router";
import Buefy from "buefy";
import "@mdi/font/css/materialdesignicons.css";
import store from "./store";
import '@/scss/style.scss';

Vue.use(Buefy);
Vue.use(Notfifications);
Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
