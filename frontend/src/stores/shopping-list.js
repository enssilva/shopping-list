import { defineStore } from 'pinia'
import { api } from 'boot/axios'

export const useShoppingListStore = defineStore('shoppingList', {
  state: () => ({
    lists: [],
    currentList: null,
    loading: false
  }),

  actions: {
    // Fetch all lists for a specific user
    async fetchUserLists(userId) {
      this.loading = true
      try {
        const response = await api.get(`/lists/${userId}`)
        this.lists = response.data
      } finally {
        this.loading = false
      }
    },

    // Create a new list
    async createList(title, userId) {
      const response = await api.post('/lists/', { title, user_id: userId })
      this.lists.push(response.data)
      return response.data
    }
  }
})