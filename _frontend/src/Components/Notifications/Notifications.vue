<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import Notification from './Notification.vue';
import api from '@/api';


const notifications = ref([]);
onMounted(async () => {
	await loadNotifications()
})

async function loadNotifications() {
	const resp = await api.get('/notifications/fetch')
	notifications.value = resp.data
}
</script>



<template>
	<div class="content">
		<div class="notifications">

			<Notification v-for="notification in notifications" :data="notification" @refresh="loadNotifications()" />
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
</style>