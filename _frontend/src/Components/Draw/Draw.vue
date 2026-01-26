<script setup lang="ts">
import VueDrawingCanvas from 'vue-drawing-canvas';
import Canvas from './Canvas.js';
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import router from '../../router';
import api from '../../api';
import ColourItem from './ColourItem.vue';
import { Vue3ColorPicker } from '@cyhnkckali/vue3-color-picker';


onMounted(() => {
	if (localStorage.getItem('token') == undefined || localStorage.getItem('token') == '') {
		return router.push({ name: 'home' });
	}
});

const canvasColour = ref('000000');
const canvas = ref<InstanceType<typeof Canvas> | null>(null);

function undoCanvas() {
	canvas.value?.undo();
}
function redoCanvas() {
	canvas.value?.redo();
}



const isSending = ref(false);

const saveCanvas = async () => {
	if (isSending.value) return;
	if (!canvas.value) return;
	isSending.value = true
	const imageData = canvas.value.save();

	try {
		const { data } = await api.post('/photos/create', {
			photoName: 'pibble',
			photoType: 'drawing',
			photoData: imageData,
		});

		if ('photoID' in data) {
			console.log(`Photo ID: ${data.photoID}`)
			router.replace({ name: 'Edit', query: { id: data.photoID } });
		}


		canvas.value.clear();
		localStorage.setItem('image', '');
		// router.back();
	} catch (error: any) {
		console.error('Failed to save canvas', error.response?.data || error.message);
	}
};

// CANVAS FUNCTIONALITY
const brushRange = ref(5);
const brushSize = computed<number>(() => {
	if (brushRange.value < 1) {
		return 1;
	}
	return Number(brushRange.value);
});

const showColourPicker = ref(false);
const sizeObject = ref<HTMLElement | null>();

function saveColour(colour?: string) {
	showColourPicker.value = false;
	if (colour === undefined) {
		canvasColour.value = canvasColour.value;
		return
	} else {
		if (colour.includes('#')) {
			colour = colour.slice(0, -2);
		} else {

			canvasColour.value = `#${colour}`;
		}


		if (!recentColours.value.includes(colour)) {
			recentColours.value = canvasColour.value ? [colour.replace('#', ""), ...recentColours.value].slice(0, 6) : recentColours.value;
		}

	}

	if (sizeObject.value) {
		sizeObject.value.style.backgroundColor = colour ? canvasColour.value : '#000000';
	}



}

function localSave() {
	const baseImage = JSON.stringify(canvas.value?.getAllStrokes());
	localStorage.setItem('image', baseImage);
}

var timer: number | null = null;

onMounted(() => {
	canvasColour.value = '#000000';
	timer = setInterval(() => {
		localSave();
	}, 5000);
});

onUnmounted(() => {
	if (timer !== null) {
		clearInterval(timer);
	}
});

var initialImage = ref([]);
function loadPrevious() {
	const baseImage = localStorage.getItem('image');
	if (baseImage?.includes('{')) {
		initialImage.value = JSON.parse(baseImage);
	}
}

function clearCanvas() {
	canvas.value?.clear();
	canvas.value?.reset();
}

loadPrevious();

var recentColours = ref(["D22B2B", "0096FF", "000000", "FFFFFF", "800020", "50C878"]);


watch(brushRange, changeSizeObject);
function changeSizeObject(newval: number) {
	if (sizeObject.value) {
		sizeObject.value.style.width = `${brushSize.value}px`;
		sizeObject.value.style.height = `${brushSize.value}px`;
	}
}

const CANVAS_SIZE = computed(() => {
	return window.innerWidth > 600 ? 500 : 300
})
</script>

<template>
	<div class="content">
		<div class="colour__picker" v-if="showColourPicker">
			<Vue3ColorPicker v-model="canvasColour" :disable-history="true" :show-eye-dropper="false"
				:show-color-list="true" :show-alpha="true" :mode="'solid'" :show-buttons="true" :show-input-menu="false"
				:show-input-set="false" :show-picker-mode="false" :theme="'dark'" @on-save="saveColour"
				@on-cancel="showColourPicker = false" />
		</div>


		<div class="canvas">
			<div class="overlay" v-if="isSending">
				Uploading...
			</div>
			<Canvas ref="canvas" :color="canvasColour" :line-width="brushSize" class="canvasObj" :stroke-type="'dash'"
				:height="CANVAS_SIZE" :width="CANVAS_SIZE" :initial-image="initialImage" :line-join="'round'" />
		</div>


		<div class="toolbar">
			<div class="toolbar__colours">

				<div class="colour colour--picker" @click="showColourPicker = !showColourPicker">
					<i class="pi pi-palette"></i>
				</div>
				<ColourItem v-for="colour in recentColours" :colour="colour" @colour="saveColour" />


			</div>
			<div class="toolbar__sizing">



				<input type="range" v-model="brushRange" min="0" max="50" class="size__range">
				<div class="size__container">
					<div class="size__show" ref="sizeObject"></div>
				</div>
			</div>
			<div class="toolbar__options">
				<div class="option" @click="undoCanvas"><i class="pi pi-undo"></i></div>
				<div class="option" @click="redoCanvas"><i class="pi pi-undo flip"></i></div>
				<div class="option" @click="clearCanvas"><i class="pi pi-trash"></i></div>
				<div class="option option--last" @click="saveCanvas"><i class="pi pi-send"></i></div>
			</div>
		</div>
	</div>
</template>

<style scoped lang="css">
.content {
	min-width: 300px;
	max-width: 500px;
	height: 100%;
	margin: auto;
	margin-top: 1rem;
}

.colour__picker {
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
}



.canvas {
	width: fit-content;
	height: fit-content;
	margin: auto;
}

.toolbar {
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
	width: 80%;
	margin: auto;
	margin-top: .5rem;
}

.toolbar__colours {
	display: flex;
	gap: .75rem;
	justify-content: center;

}

.overlay {
	height: 300px;
	width: 300px;
	position: absolute;
	color: black;
	background-color: rgba(0, 0, 0, 0.);
	display: flex;
	justify-content: center;
	align-items: top;
	font-weight: bold;
	font-size: 50px;
}



.colour--picker {
	background-color: var(--clr-surface-a20);
	display: flex;
	justify-content: center;
	align-items: center;

}

.colour {
	height: 2rem;
	width: 2rem;
	border-radius: 8px;
}


/* Size Slider */
.toolbar__sizing {
	display: flex;
	gap: 1rem;
	align-items: center;
	justify-content: center;
	min-height: 60px;
}

.toolbar__options {
	display: flex;
	gap: .75rem;
}

.size__range {
	accent-color: black;
}

.size__container {
	display: flex;
	justify-content: center;
	align-items: center;
	min-width: 60px;
}

.size__show {
	background-color: black;
	height: 5px;
	width: 5px;
	border-radius: 50%;

}

.option {
	height: 2rem;
	width: 2rem;
	background-color: var(--clr-surface-a20);
	display: flex;
	justify-content: center;
	align-items: center;
	border-radius: 8px;

}

.toolbar__options .option--last {
	margin-left: auto;
}

.flip {
	transform: rotateY(180deg);
}


/* .colours {
	display: flex;
	gap: 1rem;
	width: 100%;
}

.reverse {
	
}


.actions {
	margin-top: 0.5rem;
	display: flex;
	justify-content: space-around;
	align-items: center;
}

.content {
	margin: auto;
	margin-top: 1rem;
	display: flex;
	flex-direction: column;
	justify-content: center;
	width: fit-content;
} */

@media only screen and (max-width: 768px) {
	.content {
		width: 100%;
	}
}
</style>
