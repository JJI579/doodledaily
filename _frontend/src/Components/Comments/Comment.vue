<script lang="ts" setup>
import api from '@/api';
import type { CommentReturn, UserReturn } from '@/types';
import { computed, onMounted, ref, type PropType } from 'vue';

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

onMounted(async () => {
	try {
		const { data } = await api.get(`/users/${props.comment.userID}/fetch`);
		user.value = data;
	} catch (error: any) {
		console.error('Failed to fetch user', error.response?.data || error.message);
	}
});
</script>

<template>
	<div class="comment">
		<div class="left">
			<div class="author">
				<b>{{ user?.userName }}</b>
			</div>
			<div class="content">
				{{ props.comment.comment }}
			</div>
		</div>
		<div class="right">
			<i>{{ relativeTime }}</i>
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

.left {
	display: flex;
	flex-direction: column;
	gap: 0.25rem;
}

.right {
	color: var(--clr-surface-a50);
	font-size: small;
}
</style>
