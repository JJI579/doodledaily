import { defineStore } from "pinia";
import { ref } from "vue";

export const useCommentModel = defineStore('comments', () => {
	const showRef = ref(false);
	const photoID = ref(-1);

	function show(comment: number) {
		photoID.value = comment
		showRef.value = true
	}

	function closePage() {
		showRef.value = false
		photoID.value = -1
	}

	return { show, photoID, closePage, showRef }
})