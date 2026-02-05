const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue'), meta: { requiresAuth: true } },
      { path: 'product-catalog', name: 'product-catalog', component: () => import('pages/ProductCatalogPage.vue'), meta: { requiresAuth: true } },
      { path: 'add-product', name: 'add-product', component: () => import('pages/AddProductPage.vue'), meta: { requiresAuth: true } },
      { path: 'shopping-list', name: 'shopping-list', component: () => import('pages/ShoppingListPage.vue'), meta: { requiresAuth: true } },
      { path: 'shopping-list/:id', name: 'list-details', component: () => import('pages/ListDetailsPage.vue'), meta: { requiresAuth: true } },
      { path: 'create-list', name: 'create-list', component: () => import('pages/CreateListPage.vue'), meta: { requiresAuth: true } },
      { path: 'markets', name: 'markets', component: () => import('pages/MarketsPage.vue'), meta: { requiresAuth: true } }
    ]
  },
  
  { path: '/login', component: () => import('pages/LoginPage.vue') },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
