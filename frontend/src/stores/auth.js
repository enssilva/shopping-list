import { defineStore } from 'pinia'
import { AuthService } from 'src/services/AuthService'
// Importação removida do corpo da função para evitar erros de escopo

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Tenta recuperar o usuário já convertido em objeto
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    token: (state) => state.user?.access_token,
    userId: (state) => state.user?.id,
    // Ajustado para garantir que pega o nome correto para o sidebar
    userName: (state) => state.user?.full_name || state.user?.name || 'User'
  },

  actions: {
    async login(email, password) {
      this.loading = true
      try {
        const userData = await AuthService.login({ email, password })
        this.user = userData
        
        // Persistência segura
        localStorage.setItem('user', JSON.stringify(userData))
        return userData
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      localStorage.removeItem('user')
      
      // Em vez de usar this.router (que pode falhar), 
      // o redirecionamento deve ser feito no componente ou index.js
      // ou use a solução global do Quasar se configurada.
    }
  }
})