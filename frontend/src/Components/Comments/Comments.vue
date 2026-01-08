<script lang="ts" setup>
import { nextTick, onMounted, ref } from 'vue';

import Comment from './Comment.vue';
import api from '@/api';
import { type CommentReturn } from '@/types';
import router from '@/router';




const props = defineProps({
	id: {
		type: Number,
		required: true,
	},
});


const comments = ref<CommentReturn[]>([]);


async function loadComments(photoID: number) {
	try {
		const { data } = await api.get(`/photos/${photoID}/comments`);
		if ('detail' in data) {
			console.log(data.detail);
			return;
		}

		comments.value = data;



	} catch (error: any) {
		console.error('Failed to fetch comments', error.response?.data || error.message);
	}
}

onMounted(() => {
	if (localStorage.getItem('token') == undefined || localStorage.getItem('token') == '') {
		return router.push({ name: 'home' });
	}

	const params = new URLSearchParams(window.location.search);
	const photoID = Number(params.get('id'));
	loadComments(photoID);


});

const message = ref();
const commentsRef = ref();

const submit = async () => {
	// Get photoID from URL
	const params = new URLSearchParams(window.location.search);
	const photoID = params.get('id');
	if (!photoID || !message.value.trim()) return;

	try {
		// POST comment
		await api.post(`/photos/${photoID}/comments/create`, {
			comment: message.value,
		});

		await loadComments(Number(photoID));
		await nextTick();
		commentsRef.value.scroll({
			top: commentsRef.value.scrollHeight,
			behaviour: 'smooth'
		})


		message.value = '';
	} catch (error: any) {
		console.error('Failed to submit comment', error.response?.data || error.message);
	}
};



</script>

<template>
	<div class="content" :class="{ 'content--flex': comments.length == 0 }">
		<div class="comments" v-if="comments.length > 0" ref="commentsRef">
			<Comment v-for="comment in comments" :key="comment.commentID" :comment="comment" />
		</div>
		<div v-else class="nothing">
			<h2 class="nothing__1">No Comments...</h2>
			<h3 class="nothing__2">Make a guess?</h3>
		</div>
	</div>

	<div class="create__comment">
		<input type="text" v-model="message" class="create__comment__input" />
		<input type="submit" value="Send" @click="submit()" />
	</div>
</template>

<style lang="css" scoped>
.content {
	height: 85%;
	width: 90%;
	margin: auto;
	margin-top: 3rem;
}

.comments {
	min-height: 0;
	flex: 1;

	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}

.content--flex {
	display: flex;
	justify-content: center;
	align-items: center;
}

.create__comment {
	width: 80%;
	margin-inline: 0.25rem;
	position: sticky;
	bottom: 0;
	display: block;
	display: flex;
	gap: 0.5rem;
	margin: auto;
}

.create__comment__input {
	font-size: 16px;
	height: 2rem;
	flex: 1;
}

.nothing {
	display: flex;
	flex-direction: column;
	justify-content: center;
	gap: 0.5rem;
	align-items: center;
}

.nothing__1 {
	margin: 0;
}

.nothing__2 {
	margin: 0;
}

@media (min-width: 1024px) {
	.content {
		width: 30%;
		margin: auto;
	}

	.create__comment {
		width: 30%;
	}

	.comments {
		padding-top: 2rem;
		gap: .5rem;
	}

}
</style>
