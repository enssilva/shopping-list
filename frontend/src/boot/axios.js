import { boot } from 'quasar/wrappers'
import axios from 'axios'

// process.env is used for Quasar CLI, 
// but for Vite-based Quasar, we use import.meta.env
const api = axios.create({ 
  baseURL: import.meta.env.VITE_API_URL 
})

export default boot(({ app }) => {
  // Interceptador de Requisição: Adiciona o Token
  api.interceptors.request.use(
    (config) => {
      // Recuperamos o token do seu store de autenticação
      const token = localStorage.getItem('access_token') // Ou use store.auth.token
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Interceptador de Resposta: Trata erros de autenticação
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      // Se o backend retornar 401 (Não autorizado), redireciona para login
      if (error.response && error.response.status === 401) {
        // Lógica para limpar o localStorage e redirecionar para /login
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      return Promise.reject(error)
    }
  )

  app.config.globalProperties.$api = api
})

export { api }