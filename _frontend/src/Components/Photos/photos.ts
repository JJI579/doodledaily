import api from "@/api";
import { type PhotoReturn } from "@/types";
import { defineStore } from "pinia";
import { ref } from "vue";

export const usePhotoStore = defineStore('photos', () => {
	const photos = ref<PhotoReturn[]>([]);
	var lastFetched = '';

	async function fetch() {
		try {
			let res;
			if (lastFetched == '') {
				res = await api.get('/photos/fetch');
				photos.value = res.data
			} else {
				res = await api.get(`/photos/fetch?after=${lastFetched}`);
				// ensure no duplicates 
				const noCopy = res.data.filter((photo: PhotoReturn) => {
					return !photos.value.includes(photo)
				})
				console.log(noCopy)
				photos.value = photos.value.concat(noCopy).sort((a: PhotoReturn, b: PhotoReturn) => {
					return new Date(b.photoCreatedAt).getTime() - new Date(a.photoCreatedAt).getTime();
				})

			}
			lastFetched = new Date().toISOString()
		} catch (err) {
			console.error(err);
		}
	}

	async function hardFetch() {
		// instead of fetching using query of time, force fetch all images
		try {
			const res = await api.get('/photos/fetch');
			photos.value = res.data;
		} catch (err) {
			console.error(err);
		}
	}

	// init photos...
	fetch()

	return { photos, fetch }
})