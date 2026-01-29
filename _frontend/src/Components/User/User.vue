<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import router from '../../router';
import api from '../../api';
import { type PhotoReturn, type FriendUserReturn } from '../../types';
import type { AxiosError } from 'axios';
import Image from './Image.vue';
import { useUserModel } from '../Photos/user';
import { useRoute } from 'vue-router';
import { useCommentModel } from '../Photos/comment';



const user = ref<FriendUserReturn>();
const userID = ref(-1);


const photoArray = ref<PhotoReturn[]>([]);

const route = useRoute();

async function initPage() {
	const userParam = route.query.id || null;

	if (userParam == null) {
		router.push({ name: 'home' });
	} else {
		userID.value = Number(userParam)
		const userResp = await api.get(`/users/${userParam}/fetch?checkfriend=true`)
		user.value = userResp.data
		const photoResp = await api.get(`/photos/fetch?user=${userParam}`)
		photoArray.value = photoResp.data
	}
}

watch(() => route.query.id, async () => {
	await initPage()
})

onMounted(async () => {
	await initPage()
})

const photoData = "true"

async function requestFriend() {
	if (userID.value !== -1) {
		try {
			await api.post(`/friends/${userID.value}/request`)
		} catch (error) {
			const errorObj = (error as AxiosError).response?.data;
			if (errorObj && typeof errorObj === 'object' && "detail" in errorObj) {
				console.log((errorObj as Record<string, unknown>).detail)
			}
		}
	}
}

const userStore = useUserModel();


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
			<button class="button" @click="requestFriend()"
				:class="{ 'button--active': !userStore.friendsDict.get(user?.userID) && !(user?.userID == userStore.user?.userID) }">Add
				Friend
			</button>

		</div>
		<div class="posts">

			<Image v-for="photo in photoArray" :key="photo.photoID" :image="photo" />
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
	display: none;
}

.button--active {
	display: initial;
}

.settingsButtonContainer {
	width: 100%;
	display: flex;
	justify-content: flex-end;
}

.settingsButton {
	/* position: fixed; */
	color: white;
	top: 10px;
	right: 10px;
	background-color: transparent;
	border: none;
	font-size: 24px;
	cursor: pointer;
	display: none;
}

.settingsButton--active {
	display: initial;
}

.posts {
	justify-content: center;
	width: fit-content;
	margin: auto;
	margin-top: 1rem;
	display: flex;
	flex-basis: 33.33%;
	flex-wrap: wrap;
	gap: 3px;
}
</style>
