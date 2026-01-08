<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import SearchResult from './SearchResult.vue';
import api from '@/api';

const results = ref([]);
onMounted(async () => {
	const resp = await api.get('/users/fetch')
	results.value = resp.data;
})

</script>



<template>
	<div class="content">
		<div class="input">
			<label for="name"></label>
			<input type="text" id="name" name="name" placeholder="Enter Username...">
		</div>

		<div class="results">
			<SearchResult v-for="result in results" :data="result" />
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
	margin-block: .5rem;
}

.results {
	display: flex;
	flex-direction: column;
	gap: .5rem;
}
</style>