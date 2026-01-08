<script lang="ts" setup>
import api from '@/api';
import { enableNotifications } from '@/firebase';
import { onMounted, ref } from 'vue';


const token = ref('');
const receivedToken = ref('');
onMounted(async () => {
	const temp = await enableNotifications();
	if (temp !== null) {
		token.value = temp;
	} else {
		token.value = "No Token"
	}


	const resp = await api.get('/temp')
	if ('detail' in resp.data) {
		receivedToken.value = resp.data.detail
	} else {
		receivedToken.value = "No Token"
	}

})

const response = ref('');
async function save() {
	const resp = await api.post('/temp', {
		string: token.value
	})
	if ('detail' in resp.data) {
		response.value = resp.data.detail
	} else {
		response.value = "failed"
	}

}
</script>



<template>
	<div class="content">

		<h1>Debug</h1>

		<h2>Token</h2>
		<p>{{ token }}</p>
		{{ response }}

		<h3>Received</h3>
		<p>{{ receivedToken }}</p>
		<button @click="save">Save</button>

	</div>


</template>


<style lang="css" scoped>
.content {
	display: flex;
	justify-content: center;
	flex-direction: column;
	gap: .5rem;
	text-align: center;
	width: 80%;
	margin: auto;
}

.content>p {
	text-wrap: wrap;
}
</style>