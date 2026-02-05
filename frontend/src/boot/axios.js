import { boot } from 'quasar/wrappers'
import axios from 'axios'

// process.env is used for Quasar CLI, 
// but for Vite-based Quasar, we use import.meta.env
const api = axios.create({ 
  baseURL: import.meta.env.VITE_API_URL 
})

export default boot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

// src/boot/axios.js
api.interceptors.request.use((config) => {
  const user = JSON.parse(localStorage.getItem('user'))
  if (user && user.access_token) {
    config.headers.Authorization = `Bearer ${user.access_token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Se o servidor retornar 401 (Não autorizado), o token provavelmente expirou
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('user')
      // Redireciona para o login apenas se não estivermos já na página de login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export { api }