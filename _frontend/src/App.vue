<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import router from './router';
import api from './api';
import { enableNotifications } from './firebase';
import { usePopupModel } from './Components/Popup/popup';
import Popup from './Components/Popup/Popup.vue';


const addBackButton = computed(() => router.currentRoute.value.name !== "Photos");

function notificationsPage() {
	router.push({ name: "Notifications" });
}


onMounted(async () => {


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


	if (localStorage.getItem('userID') == null) {
		const resp = await api.get('/users/fetch/@me')
		localStorage.setItem('userID', resp.data.userID)
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

function refresh() {
	window.location.reload();
}

const holdStart = ref(0);
function wasHold() {
	const compare = new Date().getTime()
	const seconds = (compare - holdStart.value) / 1000
	if (seconds > .5) {
		router.push({ name: 'Debug' })
	}
}

const popupStore = usePopupModel();

const popupModel = computed(() => popupStore.show);

</script>

<template>
	<Teleport to="body">
		<Popup v-model="popupModel" />
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
	<RouterView />
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
</style>
