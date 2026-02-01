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

export { api }