<script lang="ts" setup>
import type { PhotoReturn } from '@/types';
import type { PropType } from 'vue';



const props = defineProps({
	image: {
		type: Object as PropType<PhotoReturn>,
		required: true
	}
})
</script>



<template>

	<div class="container">
		<div class="photo">
			<img :src="props.image.photoData" alt="?" class="img">
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