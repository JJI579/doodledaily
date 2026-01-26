<script lang="ts" setup>
import api from '@/api';
import { enableNotifications } from '@/firebase';
import type { Notification } from '@/types';
import type { PropType } from 'vue';


enum Colour {
	red = "#D22B2B",
	yellow = "#D2D22B",
	green = "#50C878"
}

const props = defineProps({
	data: {
		type: Object as PropType<Notification>,
		required: true
	}
})

const colour = () => {
	if (props.data.type === "request") {
		return Colour.yellow
	} else if (props.data.type == "friends") {
		return Colour.green
	} else {
		return Colour.red

	}
}

const emit = defineEmits(['refresh'])
async function acceptRequest() {
	if ("userID" in props.data) {
		const resp = await api.post(`/friends/${props.data.userID}/accept`)
		if ('detail' in resp.data) {
			// Accepted
			emit('refresh')
		}
	}
}

function notAllow() {
	alert('Never allowed to decline.')
}


</script>



<template>
	<div class="notification">
		
		<div class="status" :style="{ backgroundColor: colour() }">
			<!-- this is a line -->
		</div>
		<div class="content">
			<div class="name">
				{{ props.data.name }}
			</div>
			<div class="description">

				{{ props.data.description }}
			</div>
		</div>
		<div class="actions" v-if="props.data.type == 'request'">
			<button class="action decline" @click="notAllow()">Decline</button>
			<button class="action accept" @click="acceptRequest()">Accept</button>
		</div>


	</div>

</template>


<style lang="css" scoped>
.notification {
	display: flex;
	height: 5rem;
	/* background-color: pink; */
	align-items: center;
	gap: .5rem;
	width: 100%;
}



.content {
	display: flex;
	flex-direction: column;
	justify-content: center;
	gap: .25rem;
	max-width: 60vw;
}

.name {
	font-weight: bold;
}

.description {
	font-size: 15px;
	text-wrap: wrap;

	overflow-wrap: break-word;
}

.status {
	height: 75%;
	width: 2px;
	border-radius: 10px;
}

.actions {
	display: flex;
	flex-direction: column;
	gap: .5rem;
	margin-left: auto;
}
</style>