<script lang="ts" setup>
import { computed, onMounted, ref, type PropType, type Ref } from 'vue';
import type { PhotoReturn, UserReturn } from '../../types';
import router from '../../router';
import api from '../../api';
import { useUserModel } from './user';

const props = defineProps({
	photo: {
		type: Object as PropType<PhotoReturn>,
		required: true,
	},
	favourited: {
		type: Boolean,
		required: false,
		default: false,
	},
	user: {
		type: Object as PropType<UserReturn>,
		required: false
	}
});


const photoCreatedAtDate = computed(() => {
	if (typeof props.photo.photoCreatedAt === 'string') {
		return new Date(props.photo.photoCreatedAt);
	}
	return props.photo.photoCreatedAt;
});


const likesCount = computed(() => props.photo.likesCount);
const emit = defineEmits(['favourited', 'selectmenu', 'comment']);
const isFavourited = ref(props.photo.isFavourited);

const favouriteImage = async () => {
	if (!props.photo?.photoID) return;
	if (isFavourited.value) return;
	try {
		const { data } = await api.post(`/photos/${props.photo.photoID}/favourite`);
		isFavourited.value = true
		// Emit event immediately after response
		emit('favourited', props.photo.photoID);
	} catch (error: any) {
		console.error('Failed to favourite image', error.response?.data || error.message);
	}
};

const relativeTime = computed(() => {
	const time = photoCreatedAtDate.value;
	if (!time) return '';

	const now = new Date();
	let diffSeconds = Math.floor((now.getTime() - time.getTime()) / 1000);
	if (diffSeconds < 0) diffSeconds = 0;

	if (diffSeconds < 60) {
		return `${diffSeconds} second${diffSeconds === 1 ? '' : 's'} ago`;
	}

	const diffMinutes = Math.floor(diffSeconds / 60);
	if (diffMinutes < 60) {
		return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
	}

	const diffHours = Math.floor(diffMinutes / 60);
	if (diffHours < 24) {
		return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
	}

	const diffDays = Math.floor(diffHours / 24);
	return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
});


const userStore = useUserModel();

const owner: Ref<UserReturn | undefined> = ref(props.user);

onMounted(async () => {
	const token = localStorage.getItem('token');
	if (!token) {
		return router.push({ name: 'home' });
	}

	if (owner.value !== undefined) {
		console.log("Already fetched User")
		return
	}
	try {
		const data = await userStore.fetchUser(props.photo.photoOwnerID);
		owner.value = data;
	} catch (error: any) {
		console.error('Failed to fetch owner', error.response?.data || error.message);
	}
});

function goToUser() {
	router.push({ name: 'user', query: { id: props.photo.photoOwnerID } });
}

function downloadBase64Image() {
	const link = document.createElement('a');
	link.href = props.photo.photoData;
	link.download = props.photo.photoName;
	link.click();
}

// see if you can delete the photo.
const visible = props.photo.photoOwnerID === Number(localStorage.getItem('userID'));
</script>

<template>
	<div class="photo">
		<div class="author">
			<div @click="goToUser()" class="author--flex">
				<i class="pi pi-user"></i>
				<p class="text">{{ owner?.userName }}</p>
			</div>

			<div class="end" @click="emit('selectmenu', props.photo.photoID)" v-if="visible">
				<i class="pi pi-ellipsis-h"></i>
			</div>
		</div>
		<div class="photo__canvas">
			<img :src="props.photo.photoData" class="photo__img" loading="lazy" />
		</div>

		<div class="photo__content">
			<div class="photo__actions">
				<button class="button--action favourite" @click="favouriteImage()">
					<span class="pi" :class="{ 'pi-heart': !isFavourited, 'pi-heart-fill': isFavourited }"></span>
					<p class="favourite__amount">{{ likesCount }}</p>
				</button>
				<!-- <RouterLink :to="{ name: 'Comments', query: { id: props.photo.photoID } }" class="decor">
					<button class="button--action favourite">
						<span class="pi pi-comment"></span>
						<p class="favourite__amount">{{ props.photo.commentCount }}</p>
					</button>
				</RouterLink> -->

				<button class="button--action favourite" @click="emit('comment', props.photo.photoID)">
					<span class="pi pi-comment"></span>
					<p class="favourite__amount">{{ props.photo.commentCount }}</p>
				</button>

				<button class="button--action" @click="downloadBase64Image()">
					<span class="pi pi-download"></span>
				</button>
			</div>
			<div class="photo__caption">
				<div v-if="photo.photoName" class="photo__title">
					{{ photo.photoName }}
					<br>
				</div>

				{{ photo.photoCaption }}
			</div>
			<div class="photo__time">
				<p class="text">{{ relativeTime }}</p>
			</div>
		</div>
	</div>

</template>

<style lang="css" scoped>
.photo {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.5rem;

	margin: auto;

	border-radius: 3px;
	/* padding: 5px; */
}

.author--flex {
	display: flex;
	gap: 10px;
}

.author {
	text-align: left;
	width: 95%;
	height: 2rem;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.end {
	margin-right: 1rem;
}

.author__pfp {
	border-radius: 50%;
}

.button--action {
	min-height: 1rem;
	min-width: 1rem;
	background: none;
	outline: none;
	border: none;
}

.decor {
	text-decoration: none;
}

.button--action>.pi {
	font-size: 1.5rem;
	color: white;
}

.favourite {
	display: flex;
	align-items: center;
	gap: .25rem;
	text-decoration: none;
}

.favourite__amount {
	padding: 0;
	margin: 0;
	color: white;
	font-weight: bold;
	font-family: 'Roboto', sans-serif;
}

.photo__canvas {
	width: 100%;
	height: 100%;
	display: flex;
	justify-content: center;
}

.photo__img {
	width: 100%;

}

.photo__content {
	margin: auto;
	width: 95%;
	display: flex;
	flex-direction: column;
	gap: .75rem;
}

.photo__time {
	width: 95%;
	font-size: small;
	margin-bottom: 0.5rem;
	color: grey;
}

.text {
	margin: 0;
	padding: 0;
	width: 100%;
}

.photo__actions {
	display: flex;
	gap: .5rem;
	width: 100%;
}

.photo__title {
	font-weight: bold;
}

.photo__caption {
	font-size: 14px;
}

.bold {
	font-weight: bold;
}

@media (min-width: 1024px) {
	.photo__img {
		border-radius: 8px;
	}
}
</style>
