import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import mdiVue from 'mdi-vue/v3'
import * as mdijs from '@mdi/js'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { VueShowdownPlugin } from 'vue-showdown';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

createApp(App).use(router).use(pinia).use(mdiVue, {
    icons: mdijs
  }).use(VueShowdownPlugin, {
    // set default flavor of showdown
    flavor: 'github',
    // set default options of showdown (will override the flavor options)
    options: {
      emoji: false,
    },
  }).mount('#app')
