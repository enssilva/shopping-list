import { api } from 'boot/axios'

export const AuthService = {
  /**
   * Authenticates the user and returns profile data and tokens.
   */
  async login(credentials) {
    // O FastAPI geralmente envia 'access_token' e 'user' ou dados diretos
    const response = await api.post('/auth/login', credentials)
    
    // É importante retornar o objeto completo que contém o token
    return response.data
  }
}