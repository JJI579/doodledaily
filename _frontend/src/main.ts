import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import './base.css';
import '@cyhnkckali/vue3-color-picker/dist/style.css'
import 'primeicons/primeicons.css';
import './firebase';

const app = createApp(App);

app.use(router);

app.mount('#app');

// if ('serviceWorker' in navigator) {
// 	window.addEventListener('load', async () => {
// 		await navigator.serviceWorker.register('/firebase-messaging-sw.js');
// 	});
// }

