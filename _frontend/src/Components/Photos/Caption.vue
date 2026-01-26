<script lang="ts" setup>
import api from '@/api';
import { usePhotoStore } from './photos';
import { useRoute } from 'vue-router';
import { ref } from 'vue';
import router from '@/router';

const route = useRoute();
const id = Number(route.query.id);

const photoStore = usePhotoStore();

const titleModel = ref();
const textareaModel = ref();

async function submit() {
	const resp = await api.patch(`/photos/${id}/edit`, {
		title: titleModel.value,
		caption: textareaModel.value
	})

	photoStore.hardFetch();
	setTimeout(() => {
		router.replace({ name: 'Photos' });
	}, 1000);
}
</script>


<template>

	<div class="content">

		<img :src="photoStore.photoDict.get(id)?.photoData" class="photo">
		<input class="selection__input" type="text" placeholder="Add a title.." v-model="titleModel">
		<textarea class="selection__input textarea" type="text" placeholder="Add a caption..." maxlength="60"
			v-model="textareaModel"></textarea>
		<div class="pos" @click="submit">
			<i class="pi pi-check"></i>
		</div>
	</div>

</template>


<style lang="css" scoped>
.content {
	height: 100%;
	width: 80%;
	margin: auto;
	margin-top: 1rem;
	display: flex;
	flex-direction: column;
	justify-content: left;
	align-items: center;
	gap: .5rem;
}


.selection__input {
	width: 90%;
	font-family: 'Roboto', sans-serif;
	font-size: 1rem;
	padding: .375rem .75rem;
	flex: 1;
	background: none;
	border: none;
	outline: none;
	border-radius: 8px;
	background-color: var(--clr-surface-a10);
	color: white;
	padding-block: .5rem;
	line-height: 1.5rem;
}

.textarea {
	min-height: 4rem;
}

.pos {
	position: absolute;
	bottom: 10%;
	right: 5%;
	border-radius: 50%;
	background-color: var(--clr-success-a0);
	width: 3rem;
	height: 3rem;
	display: flex;
	justify-content: center;
	align-items: center;
	font-size: 20px;
}

.pos i {
	font-weight: 800;
}
</style>