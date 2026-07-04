<template>
  <el-row :gutter="16" class="demo-global-bar">
    <el-col :span="6">
      <el-select
        :model-value="demoStore.marketId"
        placeholder="选择市场"
        @change="onMarketChange"
      >
        <el-option v-if="showAllMarkets" label="🌐 全市场总览" :value="0" />
        <el-option v-for="m in demoStore.markets" :key="m.id" :label="m.name" :value="m.id" />
      </el-select>
    </el-col>
    <el-col :span="5">
      <el-select
        :model-value="demoStore.accountId"
        placeholder="选择账户"
        @change="onAccountChange"
        :disabled="showAllMarkets && demoStore.isAllMarkets"
      >
        <!-- Dashboard 模式：注入市场总览虚拟选项 -->
        <el-option
          v-if="showAllMarkets"
          v-for="a in demoStore.availableAccountsWithOverview"
          :key="a.id"
          :label="a.label"
          :value="a.id"
        />
        <!-- 非 Dashboard 模式：仅真实账户 -->
        <template v-else>
          <el-option v-for="a in demoStore.accounts" :key="a.id" :label="a.label" :value="a.id" />
        </template>
      </el-select>
    </el-col>
    <el-col :span="5">
      <el-select
        :model-value="demoStore.strategyId"
        placeholder="选择策略"
        @change="onStrategyChange"
        :disabled="showAllMarkets && (demoStore.isAllMarkets || demoStore.isMarketOverview)"
      >
        <!-- Dashboard 模式：注入账户总览虚拟选项 -->
        <template v-if="showAllMarkets">
          <el-option
            v-for="s in demoStore.availableStrategiesWithOverview"
            :key="s.id"
            :label="s.label"
            :value="s.id"
          />
        </template>
        <!-- 非 Dashboard 模式：仅真实策略 -->
        <template v-else>
          <el-option v-for="s in demoStore.availableStrategies" :key="s" :label="s" :value="s" />
        </template>
      </el-select>
    </el-col>
    <el-col :span="8" class="text-right">
      <el-tag :type="health.status === 'running' ? 'success' : 'danger'" size="large">
        系统状态：{{ health.status === 'running' ? '运行中' : '异常' }}
      </el-tag>
      <span class="health-detail">
        策略{{ health.services?.strategy === 'ok' ? '✓' : '✗' }}
        执行{{ health.services?.executor === 'ok' ? '✓' : '✗' }}
        风控{{ health.services?.risk === 'ok' ? '✓' : '✗' }}
      </span>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch } from 'vue'
import { getHealth } from '/@/api/demo/index'
import { MARKET_OVERVIEW, useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoGlobalBar' })

const props = defineProps<{ showAllMarkets?: boolean }>()
const emit = defineEmits<{
  change: []
}>()

const demoStore = useDemoStore()
const health = ref<any>({ status: 'loading', services: {} })

/** 重置为非总览状态：选第一个真实市场、第一个真实账户、第一个真实策略 */
async function resetToRealSelection() {
  const mkts = demoStore.markets
  if (mkts.length === 0) return

  // 如果当前是虚拟市场(0)，切到第一个真实市场
  if (demoStore.marketId === 0) {
    const firstMkt = mkts[0].id
    // 直接设值+拉账户，不触发 switchMarket 的总览默认逻辑
    demoStore.marketId = firstMkt
    try {
      const { getAccounts } = await import('/@/api/demo/index')
      const aRes = await getAccounts({ market_id: firstMkt })
      demoStore.accounts = aRes.data
    } catch { /* ignore */ }
  }

  // 如果当前是虚拟账户(MARKET_OVERVIEW)或账户不在当前列表中，切到第一个真实账户
  const accs = demoStore.accounts
  const currentAccValid = accs.some((a: any) => a.id === demoStore.accountId)
  if (demoStore.accountId === MARKET_OVERVIEW || !currentAccValid) {
    if (accs.length > 0) {
      demoStore.accountId = accs[0].id
    }
  }

  // 如果当前策略是虚拟值或不在当前账户的策略列表中，切到第一个真实策略
  const curAcc = accs.find((a: any) => a.id === demoStore.accountId)
  const strats: string[] = curAcc?.strategies || []
  if (demoStore.strategyId === '' || !strats.includes(demoStore.strategyId)) {
    demoStore.strategyId = strats.length > 0 ? strats[0] : ''
  }

  demoStore.switchVersion++
}

// 离开/进入 Dashboard 页面时自动切换总览模式
watch(() => props.showAllMarkets, async (isDashboard) => {
  if (isDashboard) {
    // 进入 Dashboard：如果不是全市场总览，切到市场总览
    if (demoStore.marketId !== 0 && demoStore.accountId !== MARKET_OVERVIEW) {
      demoStore.accountId = MARKET_OVERVIEW
      demoStore.strategyId = ''
      demoStore.switchVersion++
    }
  } else {
    // 离开 Dashboard：重置为真实选择
    await resetToRealSelection()
  }
})

// 市场切换
async function onMarketChange(marketId: number) {
  console.log('[DemoGlobalBar] 市场切换:', marketId)
  if (!props.showAllMarkets && marketId === 0) {
    // 非 Dashboard 不能选全市场总览，回退
    return
  }
  await demoStore.switchMarket(marketId)
  emit('change')
}

// 账户切换
function onAccountChange(accId: string) {
  console.log('[DemoGlobalBar] 账户切换:', accId)
  if (!props.showAllMarkets && accId === MARKET_OVERVIEW) return
  demoStore.switchAccount(accId)
  emit('change')
}

// 策略切换
function onStrategyChange(sid: string) {
  console.log('[DemoGlobalBar] 策略切换:', sid)
  demoStore.switchStrategy(sid)
  emit('change')
}

onMounted(async () => {
  await demoStore.fetchMarketsAndAccounts()
  if (props.showAllMarkets) {
    // Dashboard：初始默认进入市场总览
    if (demoStore.accountId !== MARKET_OVERVIEW) {
      demoStore.accountId = MARKET_OVERVIEW
      demoStore.strategyId = ''
    }
  }
  try {
    const hRes = await getHealth()
    health.value = hRes.data
  } catch { /* ignore */ }
})
</script>

<style scoped>
.demo-global-bar {
  margin-bottom: 16px;
  align-items: center;
}
.demo-global-bar .text-right {
  text-align: right;
}
.health-detail {
  margin-left: 12px;
  color: #909399;
  font-size: 13px;
}
</style>
