import { defineStore } from 'pinia'
import { AuthService } from 'src/services/AuthService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // Initialize user from localStorage if available
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    userId: (state) => state.user?.id,
    userName: (state) => state.user?.full_name
  },

  actions: {
    async login(email, password) {
      this.loading = true
      try {
        const userData = await AuthService.login({ email, password })
        this.user = userData
        // Persist user data in the browser
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
      // Redirect to login page if necessary
      this.router.push('/login')
    }
  }
})