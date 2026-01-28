<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import router from './router';
import api from './api';
import { enableNotifications } from './firebase';
import { useWebsocket } from './Websocket';
import { usePopupModel } from './Components/Popup/popup';
import Popup from './Components/Popup/Popup.vue';
import { useUserModel } from './Components/Photos/user';
import CommentOverlay from './Components/Photos/CommentOverlay.vue';
import { usePhotoStore } from './Components/Photos/photos';


const userStore = useUserModel();

const addBackButton = computed(() => router.currentRoute.value.name !== "Photos" && !router.currentRoute.value.fullPath.includes(`user?id=${userStore.user?.userID}`));

function notificationsPage() {
	router.push({ name: "Notifications" });
}

const authenticated = ref(false);

onMounted(async () => {
	const websocket = useWebsocket();
	const photoStore = usePhotoStore();
	await photoStore.fetch()

	// forces update incase app has been updated.
	var lastRefreshed = localStorage.getItem('last_refreshed');
	if (lastRefreshed == null || lastRefreshed == '') {
		localStorage.setItem('last_refreshed', new Date().getTime().toString());
		window.location.reload();
	} else {
		var dateObj = new Date(lastRefreshed)
		// if more than an hour ago
		if (new Date().getTime() - dateObj.getTime() > 60 * 60 * 1000) {
			localStorage.setItem('last_refreshed', new Date().getTime().toString());
			window.location.reload();
		}
	}

	try {
		const resp = await api.get('/users/fetch/@me')
		authenticated.value = true
		localStorage.setItem('userID', resp.data.userID)

	} catch (error) {
		console.log(error)
	}



	try {
		let platform: string = ""
		const ua = navigator.userAgent
		if (/iPad|iPhone|iPod/.test(ua) && !(window as any).MSStream) platform = 'ios';
		else if (/android/i.test(ua)) platform = 'android';
		else platform = 'web';
		const token = await enableNotifications();
		if (token) {
			await api.post('/token', { token: token, platform: platform });
		} else {
			console.log('No Token');
		}
	} catch (err) {
		console.log(err)
		return err
	}
})

const holdStart = ref(0);
function wasHold() {
	const compare = new Date().getTime()
	const seconds = (compare - holdStart.value) / 1000
	if (seconds > .5) {
		router.push({ name: 'Debug' })
	} else {
		window.location.reload();
	}
}

const popupStore = usePopupModel();
const activeScreen = computed(() => router.currentRoute.value.name);


</script>

<template>
	<Teleport to="body">
		<Popup v-model="popupStore.show" />
	</Teleport>

	<div class="menu">
		<div class="menu__content">
			<div class="title">
				<i class="pi pi-arrow-left" v-if="addBackButton" @click="router.back()"></i>
				<h3 class="title__text" @mousedown="holdStart = new Date().getTime()" @mouseup="wasHold"
					@touchstart="holdStart = new Date().getTime()" @touchend="wasHold">Pib's Pics</h3>
			</div>

			<div class="end" v-if="!addBackButton">
				<div class="menu__button temp" @click="() => router.push({ name: 'Search' })"><i
						class="pi pi-search"></i></div>
				<div class="menu__button" @click="notificationsPage()"><i class="pi pi-bell"></i>
				</div>
			</div>
		</div>
	</div>
	<CommentOverlay />
	<div class="content">
		<RouterView />
	</div>
	<div class="bottom" v-if="authenticated">

		<RouterLink class="button" :class="{ 'button--active': activeScreen == 'Photos' }" :to="{ name: 'Photos' }">
			<div class="button__icon">
				<i class="pi pi-home"></i>
			</div>
			<p class="button__title">Home</p>
		</RouterLink>
		<!-- '/user?id=' + localStorage.getItem('userID') -->
		<RouterLink class="button" :to="{ name: 'user', query: { id: userStore.user?.userID } }"
			:class="{ 'button--active': activeScreen == 'user' }">
			<div class="button__icon">
				<i class="pi pi-user"></i>
			</div>
			<p class="button__title">Profile</p>
		</RouterLink>
	</div>



</template>

<style lang="css" scoped>
.menu {
	width: 100%;
	background-color: var(--clr-surface-a0);
	position: sticky;
	top: 0;
	z-index: 99999;
}

.menu__content {
	width: 90%;
	display: flex;
	justify-content: space-between;
	margin: auto;
	align-items: center;
}

.menu__button {
	cursor: pointer;
}

.title {
	display: flex;
	gap: 1rem;
	align-items: center;
}

/* temp */
.end {
	display: flex;
	gap: 2rem;
}

.content {
	flex: 1;
	overflow: hidden;
	margin-bottom: 5.5rem;
}

.bottom {
	width: 100%;
	height: 4rem;
	background-color: var(--clr-surface-a0);
	position: absolute;
	bottom: 0;
	display: flex;
	justify-content: space-evenly;
	align-items: center;

}

.button {
	color: grey;
	display: flex;
	flex-direction: column;
	justify-content: center;
	text-align: center;
	transition: 0.5s ease all;
	cursor: pointer;
	flex: 1;
	text-decoration: none;
}


.button--active {
	color: white
}

.button__icon {
	display: flex;
	justify-content: center;
	align-items: center;
}

.button__title {
	font-size: small;
	margin: 0;
	margin-top: 5px;
}
</style>
