<script lang="ts" setup>
import api from '@/api';
import router from '@/router';



const props = defineProps({
	data: {
		type: Object,
		required: true
	}
})

async function requestUser() {
	const resp = await api.post(`/friends/${props.data.userID}/request`)
	if (resp.status == 204) {
		props.data.status = "pending"
	}
}

async function cancelRequest() {
	const resp = await api.post(`/friends/${props.data.userID}/cancel`)
	if ("detail" in resp.data) {
		props.data.status = "cancelled"
	}
}

console.log(props.data.status, props.data.userName, props.data.wasSent)

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


</script>



<template>

	<div class="result">

		<div class="result__wrapper">

			<div class="text" @click="() => router.push({ name: 'user', query: { id: props.data.userID } })">
				<div class="image">
					<img class="img" :src="props.data.userPhoto ?? 'pwa-64x64.png'">
				</div>
				<div class="name">
					{{ props.data.userName }}
				</div>
			</div>

			<div class="actions">
				<button class="action" @click="requestUser()"
					v-if="props.data.status == 'none' || props.data.status == 'declined' || props.data.status == 'cancelled'">
					<i class="pi pi-user-plus"></i>
				</button>
				<button class="action action--text action--accept" @click="acceptRequest()"
					v-else-if="props.data.wasSent == true && props.data.status == 'pending'">
					<i class="pi pi-check"></i>
				</button>
				<button class="action action--text action--cancel" @click="cancelRequest()"
					v-else-if="props.data.status == 'pending'">
					<i class="pi pi-times"></i> Cancel
				</button>


				<div v-else class="action action--friend">
					<i class="pi pi-users"></i>
				</div>
			</div>
		</div>
	</div>

</template>


<style lang="css" scoped>
.result {
	display: flex;
	border: 2px solid var(--clr-surface-a10);
	border-radius: 5px;
	box-sizing: border-box;
	height: 3rem;
	width: 100%;
	margin: auto;
}

.result__wrapper {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin: auto;
	width: 95%;
}

.text {
	display: flex;
	align-items: center;
	gap: .5rem;
}

.image {
	height: 32px;
	width: 32px;
}

.img {
	height: 100%;
	width: 100%;
	object-fit: cover;
}

.name {}

.actions {}

.action {
	height: 2rem;
	width: 2rem;
	border: none;
	border-radius: 8px;
	background-color: var(--clr-surface-a0);
	border: 2px solid white;
	box-sizing: border-box;
	display: flex;
	justify-content: center;
	align-items: center;
}

.action i {
	font-size: 16px;
	color: white;
}

.action--friend {
	border: none;
}

.action--text {
	width: fit-content;
	color: white
}

.action--accept {
	border-color: var(--clr-success-a0);
}

.action--accept i {
	color: var(--clr-success-a10);
	font-weight: bold;
}

.action--cancel {
	display: flex;
	gap: .25rem;
	border-color: var(--clr-danger-a0);
}

.action--cancel i {
	color: var(--clr-danger-a10);
}
</style>