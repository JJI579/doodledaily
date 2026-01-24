<script lang="ts" setup>
import type { PhotoReturn } from '@/types';
import type { PropType } from 'vue';
import { useCommentModel } from '../Photos/comment';

const props = defineProps({
	image: {
		type: Object as PropType<PhotoReturn>,
		required: true
	}
})

const commentStore = useCommentModel();
function openComments() {
	console.log("opening comments")
	commentStore.show(props.image.photoID)
}
</script>

<template>

	<div class="container" @click="openComments">
		<div class="photo">
			<img :src="props.image.photoData" alt="Image not found" class="img">
		</div>
	</div>

</template>

<style lang="css" scoped>
.container {
	height: 100px;
	width: 100px;
}

.img {
	height: 100%;
	width: 100%;
}
</style>