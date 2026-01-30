<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import router from '../../router';
import api from '../../api';

function logout() {
	localStorage.removeItem('token');
	localStorage.removeItem('refresh_token');
	localStorage.removeItem('userID');
	router.push({ name: 'home' });
}

async function deleteAccount() {
  try {
    await api.delete('/users/delete/@me');
    logout();
  } catch (error) {
    console.error('Error deleting account:', error);
  }
}

</script>



<template>
  <div class="content">

    <h2>Settings</h2>

    <div class="settingItems">
      <p @click="router.push({ name: 'ChangePassword' })">Change Password</p>
      <p @click="deleteAccount()">Delete Account</p>
    </div>

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

h2 {
  margin-top: 1rem;
}

.settingItems {
  margin-top: 1.5rem;
  margin-right: 1rem;
  background-color: var(--clr-surface-a0);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.1);
}

.settingItems p {
  margin: 0;
  padding: 1rem 1.2rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.settingItems p:not(:last-child) {
  border-bottom: 1px solid rgba(255,255,255,0.1);
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

