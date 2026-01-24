import api from "@/api";
import type { SelfReturn, UserReturnCache } from "@/types";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useUserModel = defineStore('user', () => {
	const user = ref<SelfReturn | null>(null);
	const friendsDict = ref(new Map());
	const username = ref("");
	const tempCache = ref<Map<number, UserReturnCache>>(new Map());



	async function fetch() {
		const resp = await api.get('/users/fetch/@me')
		user.value = resp.data
		user.value?.friends.forEach((friend) => friendsDict.value.set(friend.userID, friend))
		if (!user.value) return
		username.value = user.value.userName.slice(0, 1).toUpperCase() + user.value.userName.slice(1)
	}

	async function fetchUser(userID: number, forceFetch: boolean = false) {
		if (forceFetch === true) {
			const resp = await api.get(`/users/${userID}/fetch`)
			const userInfo = resp.data
			userInfo.fetchedAt = new Date().getTime();
			tempCache.value.set(userID, userInfo)
			return userInfo
		}
		const toReturn = tempCache.value.get(userID)
		console.log(tempCache.value.get(userID))
		if (!toReturn) {
			return await fetchUser(userID, true)
		}

		if (toReturn.fetchedAt + 600000 < new Date().getTime()) {
			return await fetchUser(userID, true)
		}
		return toReturn
	}
	return { user, fetch, friendsDict, username, fetchUser }
})