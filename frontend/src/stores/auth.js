import { defineStore } from 'pinia'
import { AuthService } from 'src/services/AuthService'
import { api } from 'src/boot/axios'
// Importação removida do corpo da função para evitar erros de escopo

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Tenta recuperar o usuário já convertido em objeto
    user: JSON.parse(localStorage.getItem('user')) || null,
    // Recupera o token diretamente para o estado
    accessToken: localStorage.getItem('access_token') || null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user && !!state.accessToken,
    token: (state) => state.accessToken,
    userId: (state) => state.user?.id,
    // Ajustado para garantir que pega o nome correto para o sidebar
    userName: (state) => state.user?.full_name || 'User'
  },

  actions: {
    async restoreSession() {
      this.loading = true
      try {
        // Aqui a rota /me é chamada através da instância api do axios.js
        const response = await api.get('/users/me') 
        this.user = response.data
        
        // Atualiza o localStorage para manter os dados sincronizados
        localStorage.setItem('user', JSON.stringify(response.data))
        return response.data
      } catch (error) {
        this.logout() // Se o token estiver expirado, limpa tudo
        throw error
      } finally {
        this.loading = false
      }
    },
    async login(email, password) {
      this.loading = true
      try {
        const response = await AuthService.login({ email, password })
      
        // Armazenamos tanto os dados do usuário quanto o token
        this.user = response.user
        this.accessToken = response.access_token 

        // Persistimos o token para o axios.js conseguir ler após o F5
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        return response
      } catch (error) {
        this.logout()
        throw error
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.accessToken = null
      localStorage.removeItem('user')
      localStorage.removeItem('access_token') // Limpa o token
      this.router.push('/login')
    }
  }
})