import { defineRouter } from '#q-app/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from 'src/stores/auth' // Importe seu store

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  // A Lógica de redirecionamento entra aqui
  Router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // Se a rota exige login e o usuário não está autenticado
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      }) // Força o login
    } else {
      next() // Permite a passagem
    }
  })

  return Router
})
