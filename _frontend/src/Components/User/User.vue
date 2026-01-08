<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import router from '../../router';
import api from '../../api';
import { type FriendUserReturn } from '../../types';
import type { AxiosError } from 'axios';



const user = ref<FriendUserReturn>();
const userID = ref(-1);


onMounted(async () => {
	const params = new URLSearchParams(window.location.search);
	const userParam = params.get('id');
	if (userParam == null) {
		router.push({ name: 'home' });
	} else {
		userID.value = Number(userParam)
		const resp = await api.get(`/users/${userParam}/fetch?checkfriend=true`)
		console.log(resp)
		user.value = resp.data

	}

})

const photoData = "true"

async function requestFriend() {
	if (userID.value !== -1) {
		try {
			const resp = await api.post(`/friends/${userID.value}/request`)
			console.log(resp.data)
		} catch (error) {
			const errorObj = (error as AxiosError).response?.data;
			if (errorObj && typeof errorObj === 'object' && "detail" in errorObj) {
				console.log((errorObj as Record<string, unknown>).detail)
			}
		}
	}
}
</script>



<template>

	<div class="content">
		<div class="user">
			<div class="user__image">
				<img class="image" src="../../../public/pwa-512x512.png" alt="Profile Picture" v-if="photoData">
				<i class="image--alt pi pi-user" v-else></i>
			</div>
			<div class="user__name">
				<h2 class="name">{{ user?.userName }}</h2>
			</div>
			<button class="button" @click="requestFriend()">Add Friend</button>

		</div>
		<div class="posts">
			<!-- grid based 3x3 -->

		</div>
	</div>
</template>


<style lang="css" scoped>
.content {
	margin: auto;
	width: 90%;
	height: 100%;
}

.user {
	margin-top: 2rem;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	gap: 1rem;
}

.user__name>.name {
	padding: 0;
	margin: 0;
}

.user__image {
	height: 80px;
	width: 80px;
	overflow: hidden;
	border-radius: 15px;
}

.image {
	height: 100%;
	width: 100%;
	object-fit: cover;

}

.image--alt {
	font-size: 50px;
}

.button {
	padding-inline: 10px;
	border-radius: 10px;
	font-size: 14px;
	width: 100px;
	min-height: 40px;
	outline: none;
	border: none;

}
</style>
