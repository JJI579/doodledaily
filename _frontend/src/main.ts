import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import './base.css';
import '@cyhnkckali/vue3-color-picker/dist/style.css'
import 'primeicons/primeicons.css';
import './firebase';
import { createPinia } from 'pinia';
import { useWebsocket } from './Websocket';

const pinia = createPinia();
const app = createApp(App);

window.addEventListener('beforeunload', () => {
	const websocket = useWebsocket()
	websocket.disconnect()
});
app.use(router);
app.use(pinia)
app.mount('#app');

// if ('serviceWorker' in navigator) {
// 	window.addEventListener('load', async () => {
// 		await navigator.serviceWorker.register('/firebase-messaging-sw.js');
// 	});
// }

