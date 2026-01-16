import { defineStore } from "pinia";
import { ref } from "vue";

export const usePopupModel = defineStore('popup', () => {
	const show = ref(false);
	const message = ref('');

	function showPopup(str: string) {
		message.value = str
		console.log(message.value)
		show.value = true

	}
	return { show, message, showPopup }
})