import App from '@/App.vue';
import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/Components/Login/Login.vue';
import Draw from '@/Components/Draw/Draw.vue';
import Photos from '@/Components/Photos/Photos.vue';
import User from '@/Components/User/User.vue';
import Notifications from '@/Components/Notifications/Notifications.vue';
import Comments from '@/Components/Comments/Comments.vue';
import Debug from '@/Components/Debug.vue';
import Search from '@/Components/Search/Search.vue';

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: '/',
			name: 'home',
			component: Login,
		},
		{
			path: '/user',
			name: 'user',
			component: User,
		},
		{
			path: '/photos',
			name: 'Photos',
			component: Photos,
		},
		{
			path: '/draw',
			name: 'draw',
			component: Draw,
		},
		{
			path: '/comments',
			name: 'Comments',
			component: Comments,
		},
		{
			path: '/notifications',
			name: "Notifications",
			component: Notifications
		},
		{
			path: '/debug',
			name: 'Debug',
			component: Debug
		},
		{
			path: '/search',
			name: 'Search',
			component: Search
		}
	],
});

export default router;
