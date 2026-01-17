import type { WebsocketPacket } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";

export const usePopupModel = defineStore('popup', () => {
	const show = ref(false);
	const message = ref('');
	const data = ref<WebsocketPacket | undefined>();
	const queue = ref<String[]>([]);
	var running = ref(false);

	function showPopup(str: string, clickRoute: WebsocketPacket | undefined = undefined ) {
		if (!running.value) {
			running.value = true
			message.value = str
			data.value = clickRoute
			show.value = true
			setTimeout(() => {
				running.value = false
				const val = queue.value.shift()
				if (val !== undefined) {
					showPopup(val as string)
				}
			}, 2500);
		} else {
			queue.value.push(str)
		}
	}
	return { show, message, showPopup, data }
})