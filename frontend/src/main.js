import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import mdiVue from 'mdi-vue/v3'
import * as mdijs from '@mdi/js'
import { createPinia } from 'pinia'


const pinia = createPinia();

createApp(App).use(router).use(pinia).use(mdiVue, {
    icons: mdijs
  }).mount('#app')
