import { api } from 'boot/axios'

export const AuthService = {
  /**
   * Authenticates the user and returns profile data.
   * @param {Object} credentials - { email, password }
   */
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
    return response.data
  }
}