import { api } from 'boot/axios'

export const MarketService = {
  // Get all registered markets
  async listAll() {
    const response = await api.get('/markets/')
    return response.data
  },

  // Create a new market
  async create(marketData) {
    const response = await api.get('/markets/', marketData)
    return response.data
  }
}