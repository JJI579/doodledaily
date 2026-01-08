<script lang="ts" setup>
import api from '@/api';
import router from '@/router';
import type { CommentReturn } from '@/types';
import { nextTick, onMounted, ref, Transition, watch } from 'vue';
import Comment from '../Comments/Comment.vue';


const emit = defineEmits(['update:modelValue'])
const props = defineProps({
	modelValue: {
		type: Boolean,
		required: true
	},
	id: {
		type: Number,
		required: true
	}
})



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

watch(() => props.id, (newval) => {
	if (localStorage.getItem('token') == undefined || localStorage.getItem('token') == '') {
		return router.push({ name: 'home' });
	}
	loadComments(props.id);
})



const message = ref();
const commentsRef = ref();

const submit = async () => {
	// Get photoID from URL
	const photoID = props.id;

	try {
		// POST comment
		await api.post(`/photos/${photoID}/comments/create`, {
			comment: message.value,
		});

		await loadComments(Number(photoID));
		await nextTick();
		commentsRef.value.scroll({
			top: commentsRef.value.scrollHeight + 5,
			behaviour: 'smooth'
		})

		message.value = '';
	} catch (error: any) {
		console.error('Failed to submit comment', error.response?.data || error.message);
	}
};


function removeParam() {
	const url = new URL(window.location.href);
	url.searchParams.delete('showComment');
	window.history.replaceState({}, '', url);
	emit('update:modelValue', false)
}
</script>



<template>

	<Teleport to="body">
		<div class="popup__wrapper" @click.self="removeParam" :class="{ 'popup--active': props.modelValue }">
			<div class="popup">
				<div class="popup__content">

					<div class="comments" v-if="comments.length > 0" ref="commentsRef">
						<Comment v-for="comment in comments" :key="comment.commentID" :comment="comment" />

					</div>
					<div v-else class="nothing">
						<h2 class="nothing__1">No Comments...</h2>
						<h3 class="nothing__2">Make a guess?</h3>
					</div>


					<div class="create__comment">
						<input type="text" v-model="message" class="create__comment__input" />
						<div class="submit" @click="submit()"><i class="pi pi-send"></i></div>
					</div>
				</div>
			</div>
		</div>
	</Teleport>


</template>


<style lang="css" scoped>
/* wrapper to handle close on clickout */
.popup__wrapper {
	height: 100vh;
	width: 100%;
	position: fixed;
	bottom: -100%;
	left: 0;
	visibility: hidden;
	display: flex;
	justify-content: flex-end;
	flex-direction: column;
	transition: 0.5s ease all;
}

.popup--active {
	visibility: visible;
	bottom: 0;
}

.popup {
	width: 100%;
	height: 60vh;
	background-color: var(--clr-surface-a10);
	top: 100%;
	border-top-left-radius: 40px;
	border-top-right-radius: 40px;

}

.popup__content {
	padding: 1rem;
	padding-bottom: 0;
	height: 55vh;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	margin-inline: .5rem;
}



.comments {
	display: flex;
	flex-direction: column;
	max-height: 45vh;
	overflow-y: scroll;
	gap: 0.5rem;
	margin-top: 1rem;
	scroll-behavior: smooth;
	padding-bottom: 2rem;
}

.content--flex {
	display: flex;
	justify-content: center;
	align-items: center;
}

.create__comment {
	width: 100%;
	display: flex;
	justify-content: center;
	align-content: center;
	gap: .5rem;
}

.create__comment__input {
	font-size: 16px;
	height: 2rem;
	flex: 1;

}

.submit {
	height: 100%;
	box-sizing: border-box;
	border: 2px solid white;
	aspect-ratio: 1;
	display: flex;
	justify-content: center;
	align-items: center;
	border-radius: 8px;
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