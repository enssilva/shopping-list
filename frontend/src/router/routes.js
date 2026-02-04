const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'login', component: () => import('pages/LoginPage.vue') },
      { path: 'product-catalog', name: 'product-catalog', component: () => import('pages/ProductCatalogPage.vue') },
      { path: 'add-product', name: 'add-product', component: () => import('pages/AddProductPage.vue') },
      { path: 'shopping-list', name: 'shopping-list', component: () => import('pages/ShoppingListPage.vue') },
      { path: 'shopping-list/:id', name: 'list-details', component: () => import('pages/ListDetailsPage.vue') },
      { path: 'create-list', name: 'create-list', component: () => import('pages/CreateListPage.vue') },
      { path: 'markets', name: 'markets', component: () => import('pages/MarketsPage.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
