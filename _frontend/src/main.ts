import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';

import './base.css';
import '@cyhnkckali/vue3-color-picker/dist/style.css'
import 'primeicons/primeicons.css';
import './firebase';


const app = createApp(App);
const pinia = createPinia();

app.use(pinia)
app.use(router);
app.mount('#app');

