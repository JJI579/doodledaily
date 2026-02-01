<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import router from '../../router';
import api from '../../api';
import { errorMessages } from 'vue/compiler-sfc';
import { useUserModel } from '../Photos/user';

const username = ref('');
const confirmUsername = ref('');
const hasChecked = ref(false);
const error = ref('');
const userStore = useUserModel();


async function changeUsername() {

    hasChecked.value = true;
    if (username.value === '' || confirmUsername.value === '') {
        error.value = 'Please fill in all fields.';
        console.log(error.value);
        return;
    }

    if (username.value !== confirmUsername.value) {
        error.value = 'Usernames do not match.';
        console.log(error.value);
        return;
    }

    if (username.value === userStore.username) {
        error.value = 'New username must be different from the current username.';
        console.log(error.value);
        return;
    }

    console.log("Changing username to ", username.value);

    // Add the backend functionality
    try {
        await api.post('/users/change-username/@me?new_username=' + username.value);

        router.push({ name: 'Settings' });
    }
    catch (err: any) {
        if (err.response?.data?.detail) {
            error.value = err.response.data.detail;
            return;
        }
    }
}

</script>

<template>
    <div class="content">
    
        <h2>Change Username</h2>

        <div class="alert" v-if="error">
			<span class="pi pi-exclamation-circle icon"></span>
		    <h4>{{ error }}</h4>
        </div>
    
        <div class="settingItems">
            <h3>New Username:</h3>
            <input class="form__input" type="text" v-model="username" name="username"
				:class="{ error: username == '' && hasChecked }" />
            <h3>Confirm New Username:</h3>
            <input class="form__input" type="text" v-model="confirmUsername" name="confirmUsername"
				:class="{ error: confirmUsername == '' && hasChecked }" />
            <br>
            <button class="form__button" @click="changeUsername()">Change Username</button>
        </div>
    
    </div>
</template>


<style scoped>

.content {
  margin: auto;
  width: 90%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  padding-top: 1rem;
}

h2 {
  margin-bottom: 1.5rem;
}

.settingItems {
  background-color: var(--clr-surface-a0);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 1px solid rgba(255,255,255,0.1);
}

.settingItems h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  opacity: 0.8;
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
    margin-bottom: 1rem;
}

.form__input {
  background-color: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  color: white;
  font-size: 14px;
  outline: none;
}

.form__input:focus {
  border-color: rgba(255,255,255,0.4);
}

.form__input.error {
  border-color: rgb(183, 1, 1);
}

.form__button {
  margin-top: 1rem;
  background-color: var(--clr-surface-a0);
  border: 2px solid white;
  color: white;
  padding: 0.6rem;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  transition: 0.2s ease;
}

.form__button:hover {
  opacity: 0.8;
}

</style>