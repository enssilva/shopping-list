<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="flex flex-center bg-grey-2">
        <q-card style="width: 100%; max-width: 400px; padding: 15px" class="shadow-2">
          <q-card-section class="text-center">
            <q-avatar size="100px" font-size="52px" color="primary" text-color="white" icon="lock" class="q-mb-md" />
            <div class="text-h5 text-weight-bold">Grocery App</div>
            <div class="text-subtitle2 text-grey-7">Faça login para gerenciar seus preços em Vitória</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit="handleLogin" class="q-gutter-md">
              <q-input
                v-model="email"
                label="E-mail"
                outlined
                dense
                type="email"
                :rules="[val => !!val || 'E-mail é obrigatório']"
              >
                <template v-slot:prepend>
                  <q-icon name="email" />
                </template>
              </q-input>

              <q-input
                v-model="password"
                label="Senha"
                outlined
                dense
                type="password"
                :rules="[val => !!val || 'Senha é obrigatória']"
              >
                <template v-slot:prepend>
                  <q-icon name="lock" />
                </template>
              </q-input>

              <div>
                <q-btn
                  label="Entrar"
                  type="submit"
                  color="primary"
                  class="full-width"
                  :loading="authStore.loading"
                  unelevated
                />
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { useQuasar } from 'quasar'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const $q = useQuasar()

const email = ref('')
const password = ref('')

/**
 * Realiza o login utilizando o Pinia Store e redireciona o usuário
 */
async function handleLogin() {
  try {
    await authStore.login(email.value, password.value)
    
    $q.notify({
      color: 'positive',
      message: 'Bem-vindo de volta!',
      icon: 'check',
      position: 'top'
    })

    // Redireciona para a página que o usuário tentou acessar originalmente ou para o catálogo
    const redirectTo = route.query.redirect || '/'
    router.push(redirectTo)
  } catch (error) {
    console.error('Login error:', error)
    $q.notify({
      color: 'negative',
      message: 'Falha na autenticação. Verifique seu e-mail e senha.',
      icon: 'warning',
      position: 'top'
    })
  }
}
</script>

<style scoped>
.q-card {
  border-radius: 12px;
}
</style>