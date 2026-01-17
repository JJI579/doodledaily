<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue';
import SearchResult from './SearchResult.vue';
import api from '@/api';

const results = ref<Search[]>([]);
const inputField = ref('');

type Search = {
	userID: number;
	userName: string;
	status: string;
	userCreatedAt: string
}

async function fetchUsers() {
	const resp = await api.get('/users/fetch')
	results.value = resp.data;
}
onMounted(async () => {
	await fetchUsers()
})



const filteredResults = computed(() => {
	const query = inputField.value.toLowerCase().trim()

	if (!query) return results.value

	return results.value.filter(result => {
		return result.userName?.toLowerCase().includes(query)
	}

	)
})

// if i want to use the query parameter on the database, but if im fetching all users may aswell just make it filter the array
// const inputField = ref('');
// watch(inputField, async (newValue) => {
// 	if (newValue.length > 1) {
// 		const resp = await api.get(`/users/fetch?q=${newValue}`)
// 		console.log(resp.data)
// 		results.value = resp.data;
// 	}
// })
</script>



<template>
	<div class="content">
		<div class="input__wrapper">
			<input type="text" id="name" name="name" placeholder="Enter Username..." v-model="inputField" class="input">
		</div>

		<div class="results">
			<SearchResult v-for="result in filteredResults" :data="result" @refresh="fetchUsers" />
		</div>
	</div>


</template>


<style lang="css" scoped>
.content {
	width: 90%;
	margin: auto;
	margin-top: 1rem;
}

.input {
	flex: 1;
	margin: 0;
	padding: 0;
	height: 2rem;
	padding-left: .5rem;
}

.input__wrapper {
	display: flex;
	margin-block: 1rem;
}

.results {
	display: flex;
	flex-direction: column;
	gap: .5rem;
}
</style>