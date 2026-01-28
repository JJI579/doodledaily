<script lang="ts" setup>
import { onMounted, ref, Teleport, type Ref, nextTick, computed, watch } from 'vue';
import Photo from './Photo.vue';
import { type UserReturn, type PhotoReturn, type SelfReturn } from '../../types';
import router from '../../router';
import api from '../../api';
import CommentOverlay from './CommentOverlay.vue';
import { useCommentModel } from './comment';
import { usePhotoStore } from './photos';
import { useUserModel } from './user';


const photoStore = usePhotoStore();

const showOptions = ref(false);
const focusedPhoto = ref(-1);
function toggleOptions(photoID: number) {
	showOptions.value = !showOptions.value;
	focusedPhoto.value = photoID;
}

async function deletePost() {
	const resp = await api.post(`/photos/${focusedPhoto.value}/delete`);

	if ('detail' in resp.data) {
		showOptions.value = false
		setTimeout(() => {
			nextTick().then(() => {
				photoStore.hardFetch()
			}
			);

		}, 1000);
	}

}

const commentPage = useCommentModel()
function showComments(photoID: number) {
	commentPage.show(photoID)
}

const userStore = useUserModel();

const user = ref<SelfReturn | null>(null);
onMounted(async () => {
	await userStore.fetch();

	const params = new URLSearchParams(window.location.search);
	const commentParam = params.get('showComment')
	if (commentParam != null) {
		const commentID = Number(params.get('showComment'))
		await nextTick();
		showComments(commentID)
	}
});

const sortedPhotos = computed(() =>
	[...photoStore.photoDict.entries()].sort(
		(a, b) =>
			new Date(b[1].photoCreatedAt).getTime() -
			new Date(a[1].photoCreatedAt).getTime()
	)
)


</script>

<template>
	<div class="content">

		<div class="isTime">
			<p class="isTime__text">Hey {{ userStore.username }}, draw?</p>
			<button class="action__button long" @click="() => router.push({ name: 'draw' })">
				Draw<i class="pi pi-pencil"></i>
			</button>
		</div>
		<div class="photos">
			<Photo :photo="obj[1]" v-for="(obj, index) in sortedPhotos" class="photo" @selectmenu="toggleOptions"
				@comment="showComments" :key="obj[1].photoID" :user="userStore.friendsDict.get(obj[1].photoOwnerID)" />
		</div>
		<Teleport to="body">
			<div class="popup__wrapper">
				<div class="popup" v-if="showOptions">
					<div class="popup__content">
						<RouterLink class="popup__button" :to="{ name: 'Edit', query: { id: focusedPhoto } }">Edit
							Caption</RouterLink>
						<hr class="popup__hr">
						<button class="popup__button" @click="deletePost">Delete</button>
					</div>
				</div>
			</div>
		</Teleport>
	</div>


</template>

<style lang="css" scoped>
.photos .photo:not(:first-child) {
	margin-top: 1rem;
}

.isTime {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.5rem;
	width: 90%;
	margin: auto;
	border: 2px solid var(--clr-surface-a30);
	border-radius: 3px;
	padding: 5px;
	margin-block: 0.5rem;
	border-radius: 8px;
}

.isTime__text {
	font-size: 23px;
	font-weight: 600;
	margin-bottom: 0.5rem;
}

.action__button {
	display: flex;
	gap: .5rem;
	height: 2rem;
	justify-content: center;
	align-items: center;
	font-size: 15px;
	border: none;
	border-radius: 8px;
	background-color: #007bff;
	color: var(--clr-light-a0);
	border: 3px solid #0D3F74;
	cursor: pointer;
}

.long {
	width: 80%;
	margin-bottom: 1rem;
	height: 2.5rem;
	border-radius: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: .5rem;
	font-size: large;
	border: 2px solid var(--clr-info-a20);
}

.action__button i {
	color: var(--clr-info-a20);
}

.long {
	width: 80%;
}

.popup {
	position: absolute;
	background-color: var(--clr-surface-a0);
	height: 15%;
	width: 100%;
	bottom: -15%;
	animation: 0.2s forwards slideUp;
}



@keyframes slideUp {
	0% {
		bottom: -15%;
	}

	100% {
		bottom: 0%;
	}
}

.popup__content {
	width: 100%;
	height: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: column;
}

.popup__button {
	width: 100%;
	border: none;
	margin: auto;
	height: 40px;
	background: none;
	font-size: 16px;
	cursor: pointer;
	color: white;
	text-decoration: none;
	display: flex;
	justify-content: center;
	align-items: center;
}

.popup__hr {
	width: 80%;
	margin: 0;
	padding: 0;
}

@media (min-width: 1024px) {
	.content {
		width: 30%;
		margin: auto;
	}

	.isTime {
		margin-bottom: 2rem;
	}


}
</style>
