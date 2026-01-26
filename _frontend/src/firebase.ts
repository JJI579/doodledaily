import { getApp, getApps, initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import { getMessaging } from 'firebase/messaging';
import { getToken } from 'firebase/messaging';

const firebaseConfig = {
	apiKey: 'AIzaSyBu_tCgFuwX-qyWPEswaKNdcZxf1kihXqs',
	authDomain: 'pibble-fcefc.firebaseapp.com',
	projectId: 'pibble-fcefc',
	storageBucket: 'pibble-fcefc.firebasestorage.app',
	messagingSenderId: '370703182104',
	appId: '1:370703182104:web:3e578d39957fec3c1ed66d',
	measurementId: 'G-T1FPC5MNS6',
};

// Initialize Firebase

const firebaseApp =
	getApps().length === 0
		? initializeApp(firebaseConfig)
		: getApp();
const analytics = getAnalytics(firebaseApp);
const messaging = getMessaging(firebaseApp);

export async function enableNotifications() {
	const permission = await Notification.requestPermission();
	if (permission !== 'granted') return null;

	const token = await getToken(messaging, {
		vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY,
	});
	return token;
}
