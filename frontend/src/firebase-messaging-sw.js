importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');
import { precacheAndRoute } from 'workbox-precaching';
import { clientsClaim } from 'workbox-core';

self.skipWaiting();
clientsClaim();

precacheAndRoute(self.__WB_MANIFEST);

const firebaseConfig = {
	apiKey: 'AIzaSyBu_tCgFuwX-qyWPEswaKNdcZxf1kihXqs',
	authDomain: 'pibble-fcefc.firebaseapp.com',
	projectId: 'pibble-fcefc',
	storageBucket: 'pibble-fcefc.firebasestorage.app',
	messagingSenderId: '370703182104',
	appId: '1:370703182104:web:3e578d39957fec3c1ed66d',
	measurementId: 'G-T1FPC5MNS6',
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

// messaging.onBackgroundMessage((payload) => {
// 	const title = payload.notification?.title ?? 'Notification';
// 	const body = payload.notification?.body ?? '';
// 	const url = payload.data?.url || '/';

// 	self.registration.showNotification(title, {
// 		body,
// 		icon: '/pwa-192x192.png',
// 		badge: '/badge-72x72.png',
// 		data: { url },
// 		requireInteraction: true,
// 	});
// });

// self.addEventListener('notificationclick', (event) => {
// 	event.notification.close();
// 	const url = event.notification.data?.url || '/';
// 	event.waitUntil(
// 		clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientsArr) => {
// 			for (const client of clientsArr) {
// 				if (client.url === url && 'focus' in client) return client.focus();
// 			}
// 			return clients.openWindow(url);
// 		})
// 	);
// });
