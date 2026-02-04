<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import router from '../../router';
import api from '../../api';
import { all } from 'axios';
import { useUserModel } from '../Photos/user';
import { reduceEachLeadingCommentRange } from 'typescript';

const userStore = useUserModel();


function logout() {
	localStorage.removeItem('token');
	localStorage.removeItem('refresh_token');
	localStorage.removeItem('userID');
	router.push({ name: 'home' });
}

function changeUsername() {
  router.push({ name: 'ChangeUsername' });
}

async function deleteAccount() {
	try {
		await api.delete('/users/delete/@me');
		logout();
	} catch (error) {
		console.error('Error deleting account:', error);
	}
}

async function downloadMyPibbles() {

  console.log("Downloading my pibbles");

  const res = await api.get('/photos/download/@me', {
    responseType: 'blob',
  });

  console.log("Downloading pibbles:", res);

  const url = URL.createObjectURL(res.data);
  const link = document.createElement('a');
  link.href = url;
  link.download = userStore.username + 'Pibbles.zip';
  link.click();
}


const showOptions = ref(false);
function toggleOptions() {
  showOptions.value = !showOptions.value;
}

</script>



<template>
	<div class="content">

		<h2 class="settings">Settings</h2>

		<div class="settingItems">
      <p class="setting__item" @click="changeUsername()">Change Username</p>
			<p class="setting__item" @click="router.push({ name: 'ChangePassword' })">Change Password</p>
      <p class="setting__item" @click="downloadMyPibbles()">Download all pibbles</p>
			<p class="setting__item" @click="deleteAccount()">Delete Account</p>
		</div>

    <Teleport to="body">
			<div class="popup__wrapper">
				<div class="popup" v-if="showOptions">
					<div class="popup__content">
						<p class="popup__button__delete" @click="deleteAccount">
              Yes, I want to delete my account
            </p>
						<hr class="popup__hr">
						<button class="popup__button" @click="toggleOptions">
              No, take me back
            </button>
					</div>
				</div>
			</div>
		</Teleport>


    <div class="logoutSection">
      <button class="logoutButton" @click="logout()">Logout</button>
    </div>

	</div>
</template>


<style scoped>
.content {
	min-height: auto;
	display: flex;
	flex-direction: column;
	padding-left: 1rem;
}

.settings {
	margin-top: 1rem;
}

.settingItems {
	margin-top: 1.5rem;
	margin-right: 1rem;
	background-color: var(--clr-surface-a0);
	border-radius: 12px;
	overflow: hidden;
	border: 1px solid rgba(255, 255, 255, 0.1);
}

.settingItems .setting__item {
	margin: 0;
	padding: 1rem 1.2rem;
	cursor: pointer;
	transition: background 0.2s ease;
}

.settingItems .setting__item:not(:last-child) {
	border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logoutSection {
	margin-top: 2rem;
	display: flex;
	justify-content: center;
	padding-bottom: 2rem;
}

.logoutButton {
	background-color: var(--clr-surface-a0);
	border: 2px solid rgb(183, 1, 1);
	color: white;
	padding: 0.5rem 3rem;
	border-radius: 10px;
	cursor: pointer;
}
</style>
