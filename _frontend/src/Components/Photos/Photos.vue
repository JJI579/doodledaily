<script lang="ts" setup>
import { onMounted, ref, Teleport, type Ref, nextTick, computed } from 'vue';
import Photo from './Photo.vue';
import { type UserReturn, type PhotoReturn } from '../../types';
import router from '../../router';
import api from '../../api';
import PopupComment from './PopupComment.vue';



var images: Ref<PhotoReturn[]> = ref([]);

async function fetchImages() {
	try {
		const res = await api.get('/photos/fetch');
		images.value = res.data;
	} catch (err) {
		console.error(err);
	}
}


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
				fetchImages();
			}
			);

		}, 1000);
	}

}

const showpopup = ref(false)
const selectedComments = ref(-1);
function showComments(comment: number) {
	selectedComments.value = comment
	showpopup.value = true
}


const user = ref<UserReturn | null>(null);
onMounted(async () => {
	// Fetch Images
	await fetchImages();
	user.value = (await api.get('/users/fetch/@me')).data

	const params = new URLSearchParams(window.location.search);
	const commentParam = params.get('showComment')
	if (commentParam != null) {
		const commentID = Number(params.get('showComment'))
		await nextTick();
		showComments(commentID)
	}
});


const username = computed(() => {
	if (!user.value) return "";
	return user.value.userName.slice(0, 1).toUpperCase() + user.value.userName.slice(1)
})


</script>

<template>
	<div class="content">
		<div class="isTime">
			<p class="isTime__text">Hey {{ username }}, draw?</p>
			<button class="action__button long" @click="() => router.push({ name: 'draw' })">
				Draw<i class="pi pi-pencil"></i>
			</button>
		</div>
		<div class="photos">
			<Photo :photo="photo" v-for="photo in images" class="photo" @selectmenu="toggleOptions"
				@comment="showComments" :key="photo.photoID" />
		</div>
		<Teleport to="body">
			<div class="popup__wrapper">
				<div class="popup" v-if="showOptions">
					<div class="popup__content">
						<button class="popup__button" @click="deletePost">Delete</button>
					</div>
				</div>
			</div>
		</Teleport>
	</div>
	<PopupComment v-model="showpopup" :id="selectedComments" />


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
	align-items: flex-start;
	flex-direction: column;
}

.popup__content hr {
	width: 85%;
}

.popup__button {
	width: 50%;
	margin: auto;
	height: 40px;
	border: 2px solid var(--clr-danger-a0);
	background: none;
	border-radius: 8px;
	font-size: 16px;
	cursor: pointer;
	color: white;
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
