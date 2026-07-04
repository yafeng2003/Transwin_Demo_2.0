import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getAccounts, getMarkets } from '/@/api/demo/index'

/** 虚拟 accountId：表示"市场总览"（不选具体账户） */
export const MARKET_OVERVIEW = '_market_overview'
/** 虚拟 strategyId：表示"账户总览"（不选具体策略） */
export const ACCOUNT_OVERVIEW = '_account_overview'

export const useDemoStore = defineStore('demo', () => {
  const marketId = ref(2)
  const accountId = ref(MARKET_OVERVIEW)
  const strategyId = ref('')
  const markets = ref<any[]>([])
  const accounts = ref<any[]>([])
  /** 市场/账户/策略切换完成后的版本号，页面 watch 此值来避免竞态 */
  const switchVersion = ref(0)

  // ---------- 总览模式判断 ----------
  /** 全市场总览：marketId === 0 */
  const isAllMarkets = computed(() => marketId.value === 0)
  /** 市场总览：选定了市场但未选账户 */
  const isMarketOverview = computed(() => marketId.value !== 0 && accountId.value === MARKET_OVERVIEW)
  /** 账户总览：选定了市场+账户但未选策略 */
  const isAccountOverview = computed(() => marketId.value !== 0 && accountId.value !== MARKET_OVERVIEW && strategyId.value === ACCOUNT_OVERVIEW)
  /** 策略总览：市场+账户+策略全部选定 */
  const isStrategyOverview = computed(() => marketId.value !== 0 && accountId.value !== MARKET_OVERVIEW && strategyId.value !== ACCOUNT_OVERVIEW && strategyId.value !== '')

  // ---------- 当前市场名 & 当前账户名（用于下拉框显示） ----------
  const currentMarketName = computed(() => {
    if (marketId.value === 0) return '全市场'
    const m = markets.value.find((x: any) => x.id === marketId.value)
    return m?.name || `市场${marketId.value}`
  })
  const currentAccountLabel = computed(() => {
    const acc = accounts.value.find((a: any) => a.id === accountId.value)
    return acc?.label || acc?.name || accountId.value
  })

  // ---------- 策略列表 ----------
  const availableStrategies = computed(() => {
    const acc = accounts.value.find((a: any) => a.id === accountId.value)
    return acc?.strategies || []
  })

  /** 带虚拟选项的策略列表：前面插入"账户总览" */
  const availableStrategiesWithOverview = computed(() => {
    if (accountId.value === MARKET_OVERVIEW) return []
    return [{ id: ACCOUNT_OVERVIEW, label: `📊 ${currentAccountLabel.value}总览`, isOverview: true }, ...availableStrategies.value.map((s: string) => ({ id: s, label: s, isOverview: false }))]
  })

  /** 带虚拟选项的账户列表：前面插入"市场总览" */
  const availableAccountsWithOverview = computed(() => {
    if (marketId.value === 0) return []
    return [{ id: MARKET_OVERVIEW, label: `📊 ${currentMarketName.value}总览`, isOverview: true }, ...accounts.value.map((a: any) => ({ ...a, isOverview: false }))]
  })

  // ---------- 版本号 ----------
  function _bumpVersion() {
    switchVersion.value++
  }

  // ---------- 数据获取 ----------
  async function fetchMarketsAndAccounts() {
    try {
      const [mRes, aRes] = await Promise.all([
        getMarkets(),
        getAccounts({ market_id: marketId.value }),
      ])
      markets.value = mRes.data
      accounts.value = aRes.data
      _bumpVersion()
    } catch { /* ignore */ }
  }

  // ---------- 切换逻辑 ----------
  async function switchMarket(mkt: number) {
    marketId.value = mkt
    if (mkt === 0) {
      accountId.value = ''
      strategyId.value = ''
      _bumpVersion()
      return
    }
    try {
      const aRes = await getAccounts({ market_id: mkt })
      accounts.value = aRes.data
      // 切换市场后默认进入"市场总览"，策略下拉框禁用
      accountId.value = MARKET_OVERVIEW
      strategyId.value = ''
    } catch { /* ignore */ }
    _bumpVersion()
  }

  function switchAccount(accId: string) {
    accountId.value = accId
    if (accId === MARKET_OVERVIEW) {
      // 回到市场总览：策略下拉框禁用
      strategyId.value = ''
    } else {
      // 切换到具体账户后默认进入"账户总览"
      strategyId.value = ACCOUNT_OVERVIEW
    }
    _bumpVersion()
  }

  function switchStrategy(sid: string) {
    strategyId.value = sid
    _bumpVersion()
  }

  return {
    marketId, accountId, strategyId,
    markets, accounts,
    availableStrategies, availableStrategiesWithOverview, availableAccountsWithOverview,
    isAllMarkets, isMarketOverview, isAccountOverview, isStrategyOverview,
    currentMarketName, currentAccountLabel,
    switchVersion,
    fetchMarketsAndAccounts, switchMarket, switchAccount, switchStrategy,
  }
})
