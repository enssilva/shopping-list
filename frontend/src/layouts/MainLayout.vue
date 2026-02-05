<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />
        <q-toolbar-title> Grocery App </q-toolbar-title>
        
        <q-btn-dropdown
              flat
              round
              dense
              no-caps
            >
          <template v-slot:label>
            <q-avatar size="32px">
              <img src="https://cdn.quasar.dev/img/boy-avatar.png">
            </q-avatar>
          </template>

          <q-list style="min-width: 200px">
            <q-item>
              <q-item-section avatar>
                <q-icon name="person" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold">
                  {{ authStore.userName || '' }}
                </q-item-label>
                <q-item-label caption>Administrator</q-item-label>
              </q-item-section>
            </q-item>

            <q-separator />

            <q-item clickable v-close-popup to="/settings">
              <q-item-section avatar>
                <q-icon name="settings" size="sm" />
              </q-item-section>
              <q-item-section>Settings</q-item-section>
            </q-item>

            <q-item clickable v-close-popup @click="logout" class="text-negative">
              <q-item-section avatar>
                <q-icon name="logout" size="sm" color="negative" />
              </q-item-section>
              <q-item-section>Logout</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="bg-grey-1"
    >
      <q-list>
        <q-item-label header> Navigation </q-item-label>

        <q-item clickable to="/product-catalog">
          <q-item-section avatar>
            <q-icon name="inventory_2" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Product Catalog</q-item-label>
            <q-item-label caption>Prices and barcodes</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/shopping-list">
          <q-item-section avatar>
            <q-icon name="shopping_cart" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Shopping Lists</q-item-label>
            <q-item-label caption>Manage your lists</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/markets">
          <q-item-section avatar>
            <q-icon name="storefront" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Markets</q-item-label>
            <q-item-label caption>Register establishments</q-item-label>
          </q-item-section>
        </q-item>
        
        <q-separator q-my-md />
        
        <q-item clickable @click="logout" class="text-negative">
          <q-item-section avatar>
            <q-icon name="logout" color="negative" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Logout</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const leftDrawerOpen = ref(false)
const router = useRouter()
const authStore = useAuthStore()

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function logout() {
  authStore.logout() // Certifique-se de ter essa função no seu store
  router.push('/login')
}
</script>