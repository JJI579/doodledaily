<script lang="ts" setup>
import api from '@/api';
import { enableNotifications } from '@/firebase';
import router from '@/router';
import type { LoginReturn } from '@/types';
import type { AxiosError, AxiosResponse } from 'axios';
import { onMounted, ref } from 'vue';
api

const isLogin = ref(true);
const hasChecked = ref(false);
const username = ref('');
const password = ref('');
const error = ref('');

const login = async () => {
	error.value = '';
	hasChecked.value = true;

	if (!username.value || !password.value) {
		error.value = 'Please enter all values';
		return;
	}

	let data: LoginReturn;

	try {
		data = (await api.post('/login', {
			username: username.value,
			password: password.value,
		})).data;

		localStorage.setItem('token', data.token);
		localStorage.setItem('refresh_token', data.refresh_token);
		localStorage.setItem('userID', String(data.id));
	} catch (err: any) {

		if (err.response?.data?.detail) {
			error.value = err.response.data.detail;
			return;
		}
	}






	try {
		let platform: string = ""
		const ua = navigator.userAgent
		if (/iPad|iPhone|iPod/.test(ua) && !(window as any).MSStream) platform = 'ios';
		else if (/android/i.test(ua)) platform = 'android';
		else platform = 'web';
		const token = await enableNotifications();
		if (token) {
			await api.post('/token', { token: token, platform: platform });
		} else {
			console.log('No Token');
		}
	} catch (err) {
		console.log("eeeerr", err)
		error.value = 'Login failed. Please try again.';
	}


	router.push({ name: 'Photos' });
	window.location.reload()
};

const register = async () => {
	error.value = '';
	hasChecked.value = true;

	if (!username.value || !password.value) {
		error.value = 'Please enter all values';
		return;
	}
	try {
		const { data } = await api.post('/register', {
			username: username.value,
			password: password.value,
		});

		if ('detail' in data) {
			error.value = data.detail;
			return;
		}
		await login();
	} catch (err: any) {
		console.error('Registration failed', err.response?.data || err.message);
		error.value = 'Registration failed. Please try again.';
	}
};

function handle() {
	if (isLogin.value) {
		login();
	} else {
		register();
	}
}


function toggleLogin() {
	isLogin.value = !isLogin.value;
}

onMounted(() => {
	if (localStorage.getItem('token') != undefined && localStorage.getItem('token') != '') {
		return router.push({ name: 'Photos' });
	}
});
</script>

<template>
	<div class="content">
		<div class="form">
			<div class="alert" v-if="error">
				<span class="pi pi-exclamation-circle icon"></span>
				<h4>{{ error }}</h4>
			</div>
			<h1 class="text remove">{{ isLogin == true ? 'Login' : 'Register' }}</h1>
			<p class="remove">
				{{ isLogin == true ? 'Not Registered' : 'Already have an account' }}?
				<span @click="toggleLogin()" class="toggle">{{
					isLogin == true ? 'Register' : 'Login'
				}}</span>
			</p>

			Your Username
			<input class="form__input" type="text" v-model="username" name="username"
				:class="{ error: username == '' && hasChecked }" />
			Password
			<input class="form__input" type="password" v-model="password" name="password"
				:class="{ error: password == '' && hasChecked }" />
				
			<button @click="handle()" class="login">
				{{ isLogin == true ? 'Login' : 'Register' }}
			</button>
		</div>
	</div>
</template>

<style lang="css" scoped>
.content {
	display: flex;
	justify-content: center;
	align-content: center;
	height: 95%;
}

.error {
	border: 1px solid var(--clr-danger-a0);
}

.form {
	display: flex;
	flex-direction: column;
	gap: 1rem;
	width: 85%;
	margin: auto;
}

.form__input {
	height: 2rem;
}

.icon {
	font-size: x-large;
	color: var(--clr-danger-a0);
}

.alert {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	padding-inline: 1rem;
	background-color: var(--clr-danger-a20);
	color: black;
	border-radius: 10px;
	text-align: center;
}

.login {
	width: 5rem;
	height: 2rem;
	margin: auto;
	cursor: pointer;
}

.toggle {
	color: #0000ee;
	cursor: pointer;
}

.remove {
	margin: 0;
}
</style>
