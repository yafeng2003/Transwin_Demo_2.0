import { defineStore } from 'pinia'
import { getAccounts, getMarkets } from '/@/api/demo/index'

export const useDemoStore = defineStore('demo', () => {
  const marketId = ref(1)
  const accountId = ref('acc_main')
  const markets = ref<any[]>([])
  const accounts = ref<any[]>([])

  async function fetchMarketsAndAccounts() {
    try {
      const [mRes, aRes] = await Promise.all([getMarkets(), getAccounts()])
      markets.value = mRes.data
      accounts.value = aRes.data
    } catch {
      // ignore
    }
  }

  return { marketId, accountId, markets, accounts, fetchMarketsAndAccounts }
})
