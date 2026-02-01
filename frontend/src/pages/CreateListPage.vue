<template>
  <q-page class="q-pa-md flex flex-center">
    <q-card style="width: 100%; max-width: 400px" flat bordered>
      <q-card-section>
        <div class="text-h6">Create New Shopping List</div>
        <div class="text-subtitle2 text-grey">Organize your grocery trips</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="onCreateList" class="q-gutter-md">
          <q-input
            v-model="listName"
            label="List Name (e.g., Monthly Groceries) *"
            filled
            lazy-rules
            :rules="[val => !!val || 'Please name your list']"
          />

          <q-input
            v-model="description"
            label="Description (Optional)"
            filled
            type="textarea"
            rows="2"
          />

          <div class="row justify-end q-mt-md">
            <q-btn label="Cancel" flat color="primary" to="/shopping-list" />
            <q-btn 
              label="Create List" 
              type="submit" 
              color="primary" 
              :loading="isSubmitting" 
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { api } from 'src/boot/axios'
import { useAuthStore } from 'src/stores/auth'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const router = useRouter()
const authStore = useAuthStore()

const listName = ref('')
const description = ref('')
const isSubmitting = ref(false)

/**
 * Handles the creation of a new shopping list for Ebenezer
 */
async function onCreateList() {
  isSubmitting.value = true
  try {
    // Sending data to the /lists endpoint visible in Swagger
    const response = await api.post('/lists/', {
      name: listName.value,
      user_id: authStore.userId,
      description: description.value || null
    })

    $q.notify({
      color: 'positive',
      message: `List "${response.data.name}" created!`,
      icon: 'playlist_add_check'
    })

    // Redirecting back to the main list view
    router.push('/shopping-list')
  } catch (error) {
    console.error('Failed to create list', error)
    $q.notify({
      color: 'negative',
      message: 'Failed to create list. Try again.',
      icon: 'error'
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>