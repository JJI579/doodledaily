<script lang="ts" setup>

const props = defineProps({
	colour: {
		type: String,
		required: true
	}
})

const emit = defineEmits(['colour'])
</script>



<template>
	<div class="colour" @click="emit('colour', props.colour)" :style="{ backgroundColor: `#${props.colour}` }">
	</div>
</template>


<style lang="css" scoped>
.colour {
	height: 2rem;
	width: 2rem;
	border-radius: 8px;
}
</style>