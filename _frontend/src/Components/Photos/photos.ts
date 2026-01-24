import api from "@/api";
import { type UserReturn, type PhotoReturn } from "@/types";
import { defineStore } from "pinia";
import { reactive, ref } from "vue";

export const usePhotoStore = defineStore('photos', () => {
	const photoDict = reactive<Map<number, PhotoReturn>>(new Map());
	var lastFetched = '';


	async function fetch() {
		try {
			let res;
			if (lastFetched == '') {
				res = await api.get('/photos/fetch');
			} else {
				res = await api.get(`/photos/fetch?after=${lastFetched}`);
			}
			lastFetched = new Date().toISOString()
			res.data.forEach((element: PhotoReturn) => {
				console.log(element.photoID)
				photoDict.set(element.photoID, element)
			});
		} catch (err) {
			console.error(err);
		}
	}

	async function hardFetch() {
		// instead of fetching using query of time, force fetch all images
		try {
			const res = await api.get('/photos/fetch');
			res.data.forEach((element: PhotoReturn) => {
				photoDict.set(element.photoID, element)
			});
			lastFetched = new Date().toISOString()
		} catch (err) {
			console.error(err);
		}
	}


	return { hardFetch, fetch, photoDict }

})