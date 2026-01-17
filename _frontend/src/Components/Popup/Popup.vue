<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import { usePopupModel } from './popup';


const props = defineProps({
	modelValue: {
		type: Boolean,
		required: true,
		default: false
	}
})

const emit = defineEmits(['update:modelValue'])

let start: number | undefined = undefined;

const timer = ref<HTMLElement | undefined>();
watch(() => props.modelValue, (newval) => {
	if (newval) {
		// requestAnimationFrame(updateAnimation)
	}
})



const popupStore = usePopupModel()

const message = computed(() => popupStore.message)
function updateAnimation(timestamp: number) {

	const animationLength = 2000;

	let elapsed = timestamp - (start || (timestamp - 1));
	if (start === undefined || elapsed == -1) {
		start = timestamp;
	} else if (elapsed > (animationLength + 250)) {
		start = timestamp;

	}
	elapsed = timestamp - start;
	if (timer.value) {
		const length = Math.min(100, (elapsed / animationLength) * 100);
		timer.value.style.width = `${length}%`;
	}
	if (elapsed > animationLength) {

		popupStore.show = false
		return;
	}

	requestAnimationFrame(updateAnimation);
}
</script>



<template>

	<div class="popup__wrapper"
		:class="{ 'popup--active': props.modelValue, 'popup__wrapper--success': props.modelValue }">

		<div class="popup">
			<div class="icon icon--success">
				<i class="pi pi-question"></i>
			</div>
			<div class="text">
				{{ message }}
			</div>
		</div>


		<div class="timer" ref="timer">

		</div>
	</div>
</template>


<style lang="css" scoped>
.popup__wrapper {
	display: flex;
	flex-direction: column;
	position: absolute;
	width: 90%;
	left: 50%;
	top: -15%;
	transform: translateX(-50%);
	z-index: 1000000;
	height: 4rem;
	transition: 0.25s ease-in-out all;
	background-color: var(--clr-surface-a0);
	border-top-left-radius: 10px;
	border-top-right-radius: 10px;
}

.popup__wrapper--success {

	background-color: #19191a;
	border: 2px solid var(--clr-surface-a20);
	border-bottom: none;
	/* background: linear-gradient(rgba(0, 0, 0, 0.25), rgba(0, 0, 0, 0.25)),
		linear-gradient(90deg, #2E7049 0%, rgba(33, 31, 31, 1) 100%); */
}

.popup__wrapper--info {
	background: var(--clr-surface-a0);
	background:
		linear-gradient(rgba(0, 0, 0, 0.25), rgba(0, 0, 0, 0.25)),
		linear-gradient(90deg, #C4A117 0%, rgba(33, 31, 31, 1) 100%);
}

.icon {
	height: 32px;
	width: 32px;
	display: flex;
	justify-content: center;
	align-items: center;
	border-radius: 50%;
}


.popup--active {
	top: 2.5%;
}

.popup {
	display: flex;
	align-items: center;
	padding-inline: .5rem;
	height: 100%;
	width: 100%;
}

.text {
	flex: 1;
}

.timer {
	height: 2px;
	background-color: var(--clr-success-a0)
}

.text {
	color: white;
}
</style>