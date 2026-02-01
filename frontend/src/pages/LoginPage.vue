<template>
  <q-page class="flex flex-center bg-grey-2">
    <q-card stripe class="q-pa-md shadow-2" style="width: 400px">
      <q-card-section class="text-center">
        <div class="text-h6">Grocery System</div>
        <div class="text-subtitle2">Welcome back, Ebenezer</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="onSubmit" class="q-gutter-md">
          <q-input
            filled
            v-model="email"
            label="Email *"
            type="email"
            lazy-rules
            :rules="[val => val && val.length > 0 || 'Email is required']"
          />

          <q-input
            filled
            v-model="password"
            label="Password *"
            type="password"
            lazy-rules
            :rules="[val => val && val.length > 0 || 'Password is required']"
          />

          <div class="q-mt-md">
            <q-btn 
              label="Login" 
              type="submit" 
              color="primary" 
              class="full-width" 
              :loading="authStore.loading"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useQuasar } from 'quasar'

const authStore = useAuthStore()
const router = useRouter()
const $q = useQuasar()

const email = ref('')
const password = ref('')

async function onSubmit() {
  try {
    // Attempt login through Pinia store
    await authStore.login(email.value, password.value)
    
    $q.notify({
      color: 'positive',
      message: `Welcome, ${authStore.userName}!`,
      icon: 'check_circle'
    })

    // Redirect to home after success
    router.push('/')
  } catch (error) {
    // Now the variable is used for debugging
    console.error('Login error details:', error)
    $q.notify({
      color: 'negative',
      message: 'Login failed. Check your credentials.',
      icon: 'error'
    })
  }
}
</script>