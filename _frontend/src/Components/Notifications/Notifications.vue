<script lang="ts" setup>
import { onMounted, ref } from 'vue';

import api from '@/api';
import { enableNotifications } from '@/firebase';
import NotificationElement from './NotificationElement.vue';


const notifications = ref([]);
const notifGranted = ref(false);
onMounted(async () => {
	await loadNotifications()
	const resp = await Notification.requestPermission();
	if (resp === 'granted') {
		notifGranted.value = true
	}

})


async function loadNotifications() {
	const resp = await api.get('/notifications/fetch')

	notifications.value = resp.data
}
</script>



<template>
	<div class="content">
		<div class="prompt" v-if="!notifGranted">
			<button @click="enableNotifications" class="button">Enable Notifications</button>
		</div>
		<div class="notifications">

			<NotificationElement v-for="notification in notifications" :data="notification"
				@refresh="loadNotifications()" />
		</div>
	</div>

</template>


<style lang="css" scoped>
.content {
	width: 90%;
	margin: auto;
	margin-top: 1rem;
	height: 85vh;
	overflow-y: hidden;
}

.button {
	width: 100%;
	font-family: 'Roboto', sans-serif;
	font-size: 1rem;
	padding: .375rem .75rem;
	flex: 1;
	background: none;
	border: none;
	outline: none;
	border-radius: 8px;
	background-color: var(--clr-info-a0);
	color: white;
	padding-block: .5rem;
	line-height: 1.5rem;
}
</style>