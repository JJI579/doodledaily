<script lang="ts" setup>
import api from '@/api';
import type { CommentReturn, UserReturn } from '@/types';
import { computed, onMounted, ref, type PropType } from 'vue';
import { useUserModel } from '../Photos/user';

const props = defineProps({
	comment: {
		type: Object as PropType<CommentReturn>,
		required: true,
	},
});

const user = ref<UserReturn | null>(null);

const relativeTime = computed(() => {
	const time = new Date(props.comment.createdAt);
	if (!time) return '';

	const now = new Date();
	let diffSeconds = Math.floor((now.getTime() - time.getTime()) / 1000);
	if (diffSeconds < 0) diffSeconds = 0;

	if (diffSeconds < 60) {
		return `${diffSeconds}s ago`;
	}

	const diffMinutes = Math.floor(diffSeconds / 60);
	if (diffMinutes < 60) {
		return `${diffMinutes}m ago`;
	}

	const diffHours = Math.floor(diffMinutes / 60);
	if (diffHours < 24) {
		return `${diffHours}h ago`;
	}

	const diffDays = Math.floor(diffHours / 24);
	return `${diffDays}d ago`;
});

const hasLiked = ref(props.comment.hasLiked);

async function likeComment() {
	if (hasLiked.value) return;
	const resp = await api.post(`/photos/${props.comment.photoID}/comments/${props.comment.commentID}/like`);
	if ('detail' in resp.data) {
		props.comment.likeCount++;
		hasLiked.value = true
	}
}

const userStore = useUserModel();

onMounted(async () => {
	try {
		const data = await userStore.fetchUser(props.comment.userID);
		user.value = data;
	} catch (error: any) {
		console.error('Failed to fetch user', error.response?.data || error.message);
	}
});
</script>

<template>
	<div class="comment">
		<div class="left__side">
			<div class="left--content">
				<div class="author">
					<b>{{ user?.userName }}</b>
				</div>
				<div class="content">
					{{ props.comment.comment }}
				</div>
			</div>

		</div>
		<div class="right">
			<i>{{ relativeTime }}</i>
			<div class="liked">
				<i class="pi" @click="likeComment()" :class="{ 'pi-heart': !hasLiked, 'pi-heart-fill': hasLiked }"></i>
				{{
					props.comment.likeCount }}
			</div>
		</div>
	</div>
</template>

<style lang="css" scoped>
.comment {
	display: flex;
	justify-content: space-between;
	gap: 1rem;
	align-items: top;
}

.left--content {
	display: flex;
	flex-direction: column;
	gap: 0.25rem;
}

.left__side {
	display: flex;
	flex-direction: column;
	gap: .5rem;
}


.right {
	color: var(--clr-surface-a50);
	font-size: small;
	display: flex;
	justify-content: right;
	text-align: right;
	flex-direction: column;
	gap: .5rem;
}

.liked {
	color: white;
}

.liked i {
	cursor: pointer;
}
</style>
