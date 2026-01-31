<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue';
import router from '../../router';
import api from '../../api';
import User from '../User/User.vue';
import { useUserModel } from '../Photos/user';

const currentPassword = ref('');
const newPassword = ref('');
const confirmNewPassword = ref('');
const error = ref('');
const userStore = useUserModel();

const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmNewPassword = ref(false);


async function changePassword() {
  if (currentPassword.value === '' || newPassword.value === '' || confirmNewPassword.value === '') {
    error.value = 'Please fill in all fields.';
    return;
  }

  if (newPassword.value !== confirmNewPassword.value) {
    error.value = 'New passwords do not match.';
    return;
  }

  if (String(newPassword.value).length < 8) {
    error.value = 'New password must be at least 8 characters long.';
    return;
  }

  if (currentPassword.value === newPassword.value) {
    error.value = 'New password must be different from the current password.';
    return;
  }

  console.log("Changing password for user:", userStore.username);

  try {
    await api.post('/change-password/@me?new_password=' + newPassword.value);
    router.push({ name: 'Settings' });
  }
  catch (err: any) {
    if (err.response?.data?.detail) {
        console.log("Error changing password:", err.response.data.detail);
        error.value = err.response.data.detail;
        return;
    }
  }
}
</script>

<template>

    <div class="content">
    
        <h2>Change Password</h2>

        <div class="alert" v-if="error">
            <span class="pi pi-exclamation-circle icon"></span>
            <h4>{{ error }}</h4>
        </div>
    
        <div class="settingItems">
            <h3>Current Password:</h3>
            <div class="passwordField">
                <input class="form__input" :type="showCurrentPassword ? 'text' : 'password'" v-model="currentPassword" name="currentPassword" />
                <span class="pi" :class="showCurrentPassword ? 'pi-eye-slash' : 'pi-eye'" @click="showCurrentPassword = !showCurrentPassword"></span>
            </div>

            <h3>New Password:</h3>
            <div class="passwordField">
                <input class="form__input" :type="showNewPassword ? 'text' : 'password'" v-model="newPassword" name="newPassword" />
                <span class="pi" :class="showNewPassword ? 'pi-eye-slash' : 'pi-eye'" @click="showNewPassword = !showNewPassword"></span>
            </div>
        
            <h3>Confirm New Password:</h3>
            <div class="passwordField">
                <input class="form__input" :type="showConfirmNewPassword ? 'text' : 'password'" v-model="confirmNewPassword" name="confirmNewPassword" />
                <span class="pi" :class="showConfirmNewPassword ? 'pi-eye-slash' : 'pi-eye'" @click="showConfirmNewPassword = !showConfirmNewPassword"></span>
            </div>
        
            <br>
            <button class="form__button" @click="changePassword()">Change Password</button>
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

.passwordField {
  position: relative;
  display: flex;
  width: 100%;
  align-items: center;
}

.passwordField .form__input {
    width: 100%;
    padding-right: 2.5rem;
}

.passwordField .pi {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    cursor: pointer;
    opacity: 0.7;
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