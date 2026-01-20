import api from "@/api";
import type { SelfReturn, UserReturn } from "@/types";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useUserModel = defineStore('user', () => {
	const user = ref<SelfReturn | null>(null);
	const friendsDict = ref(new Map());
	const username = ref("");

	async function fetch() {
		const resp = await api.get('/users/fetch/@me')
		user.value = resp.data
		user.value?.friends.forEach((friend) => friendsDict.value.set(friend.userID, friend))
		if (!user.value) return
		username.value = user.value.userName.slice(0, 1).toUpperCase() + user.value.userName.slice(1)
	}

	return { user, fetch, friendsDict, username }
})