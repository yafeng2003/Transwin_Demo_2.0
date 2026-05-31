<template>
  <div class="demo-dashboard">
    <!-- 顶部栏：市场/账户选择 + 系统状态 -->
    <el-row :gutter="16" class="header-bar">
      <el-col :span="6">
        <el-select v-model="marketId" placeholder="选择市场" @change="refreshAll">
          <el-option v-for="m in markets" :key="m.id" :label="m.name" :value="m.id" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-select v-model="accountId" placeholder="选择账户" @change="refreshAll">
          <el-option v-for="a in accounts" :key="a.id" :label="a.label" :value="a.id" />
        </el-select>
      </el-col>
      <el-col :span="12" class="text-right">
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

    <!-- 资产概览卡片 -->
    <el-row :gutter="16" class="asset-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="card-label">总资产</div>
          <div class="card-value">{{ formatMoney(asset.totalAsset) }}</div>
          <div class="card-sub">净值 {{ asset.netValue?.toFixed(4) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="card-label">今日收益</div>
          <div class="card-value" :class="asset.todayPnl >= 0 ? 'up' : 'down'">
            {{ formatMoney(asset.todayPnl) }}
          </div>
          <div class="card-sub" :class="asset.todayReturnRate >= 0 ? 'up' : 'down'">
            {{ asset.todayReturnRate >= 0 ? '+' : '' }}{{ asset.todayReturnRate?.toFixed(2) }}%
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="card-label">持仓市值</div>
          <div class="card-value">{{ formatMoney(asset.marketValue) }}</div>
          <div class="card-sub">现金 {{ formatMoney(asset.cashBalance) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="card-label">累计收益</div>
          <div class="card-value" :class="asset.totalPnl >= 0 ? 'up' : 'down'">
            {{ formatMoney(asset.totalPnl) }}
          </div>
          <div class="card-sub" :class="asset.totalReturnRate >= 0 ? 'up' : 'down'">
            {{ asset.totalReturnRate >= 0 ? '+' : '' }}{{ asset.totalReturnRate?.toFixed(2) }}%
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 中间三栏 -->
    <el-row :gutter="16" class="main-row">
      <!-- 左：持仓概览 -->
      <el-col :span="14">
        <el-card class="section-card">
          <template #header>
            <span class="section-title">📊 持仓概览</span>
            <el-button text type="primary" style="float:right" @click="$router.push('/demo/strategy/positions')">
              查看全部 →
            </el-button>
          </template>
          <el-table :data="positions" stripe size="small" max-height="320">
            <el-table-column prop="symbolCode" label="代码" width="80" />
            <el-table-column prop="symbolName" label="名称" width="90" />
            <el-table-column prop="direction" label="方向" width="55">
              <template #default="{ row }">
                <el-tag :type="row.direction === 1 ? 'danger' : 'success'" size="small">
                  {{ row.direction === 1 ? '多' : '空' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="marketValue" label="市值" width="100">
              <template #default="{ row }">{{ formatMoney(row.marketValue) }}</template>
            </el-table-column>
            <el-table-column prop="weight" label="占比" width="60">
              <template #default="{ row }">{{ row.weight }}%</template>
            </el-table-column>
            <el-table-column prop="unrealizedPnl" label="浮动盈亏" width="100">
              <template #default="{ row }">
                <span :class="row.unrealizedPnl >= 0 ? 'up' : 'down'">
                  {{ formatMoney(row.unrealizedPnl) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右：持仓饼图 -->
      <el-col :span="10">
        <el-card class="section-card">
          <template #header><span class="section-title">🍩 持仓分布</span></template>
          <vab-chart :option="pieOption" style="height:340px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：风险状态 + 最近交易 -->
    <el-row :gutter="16" class="main-row" style="margin-top:16px">
      <!-- 风险状态 -->
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <span class="section-title">🛡️ 风险状态</span>
            <el-button text type="primary" style="float:right" @click="$router.push('/demo/risk/overview')">
              风控详情 →
            </el-button>
          </template>
          <el-row :gutter="12">
            <el-col :span="8">
              <div class="risk-gauge">
                <div class="risk-level" :class="'level-' + risk.riskLevel">
                  {{ ['低', '中', '高'][risk.riskLevel - 1] || '-' }}风险
                </div>
                <div class="risk-score">评分 {{ risk.riskScore }}</div>
              </div>
            </el-col>
            <el-col :span="16">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="今日事件">{{ risk.todayEvents }}</el-descriptions-item>
                <el-descriptions-item label="待处理事件">{{ risk.unresolvedEvents }}</el-descriptions-item>
                <el-descriptions-item label="最大回撤">{{ risk.maxDrawdown?.toFixed(2) }}%</el-descriptions-item>
                <el-descriptions-item label="连续亏损">{{ risk.consecutiveLosses }}次</el-descriptions-item>
              </el-descriptions>
            </el-col>
          </el-row>
        </el-card>

        <!-- 最近交易 -->
        <el-card class="section-card" style="margin-top:16px">
          <template #header>
            <span class="section-title">📋 最近交易动态</span>
            <el-button text type="primary" style="float:right" @click="$router.push('/demo/strategy/deals')">
              查看全部 →
            </el-button>
          </template>
          <el-table :data="recentDeals" stripe size="small" max-height="220">
            <el-table-column prop="symbolCode" label="代码" width="90" />
            <el-table-column prop="symbolName" label="名称" width="100" />
            <el-table-column prop="direction" label="方向" width="60">
              <template #default="{ row }">
                <el-tag :type="row.direction === 1 ? 'danger' : 'success'" size="small">
                  {{ row.direction === 1 ? '多' : '空' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="dealPrice" label="成交价" width="80">
              <template #default="{ row }">{{ row.dealPrice?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="dealQuantity" label="数量" width="80" />
            <el-table-column prop="dealAmount" label="金额" width="100">
              <template #default="{ row }">{{ formatMoney(row.dealAmount) }}</template>
            </el-table-column>
            <el-table-column prop="strategyId" label="策略" width="110" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import {
    getAccounts,
    getAssetSummary,
    getHealth,
    getMarkets,
    getPositionOverview,
    getRecentDeals,
    getRiskStatus,
} from '/@/api/demo/index'

defineOptions({ name: 'DemoDashboard' })

const marketId = ref(1)
const accountId = ref('acc_main')
const markets = ref<any[]>([])
const accounts = ref<any[]>([])
const health = ref<any>({ status: 'loading', services: {} })
const asset = ref<any>({})
const risk = ref<any>({})
const positions = ref<any[]>([])
const recentDeals = ref<any[]>([])

const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const pieOption = computed(() => {
  const pieData = positions.value.map((p: any) => ({
    value: p.marketValue,
    name: p.symbolName || p.symbolCode,
  }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 10 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '43%'],
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { formatter: '{b}\n{d}%', fontSize: 11 },
      data: pieData,
    }],
  }
})

async function refreshAll() {
  const [mRes, aRes, hRes, aSumRes, posRes, rRes, dRes] = await Promise.all([
    getMarkets(), getAccounts(), getHealth(),
    getAssetSummary({ market_id: marketId.value, account_id: accountId.value }),
    getPositionOverview({ market_id: marketId.value, account_id: accountId.value }),
    getRiskStatus({ market_id: marketId.value, account_id: accountId.value }),
    getRecentDeals({ market_id: marketId.value, limit: 10 }),
  ])
  markets.value = mRes.data
  accounts.value = aRes.data
  health.value = hRes.data
  asset.value = aSumRes.data
  positions.value = posRes.data.positions
  risk.value = rRes.data
  recentDeals.value = dRes.data
}

onMounted(refreshAll)
</script>

<style scoped>
.demo-dashboard { padding: 16px; }
.header-bar { margin-bottom: 16px; align-items: center; }
.header-bar .text-right { text-align: right; }
.health-detail { margin-left: 12px; color: #909399; font-size: 13px; }
.asset-cards { margin-bottom: 16px; }
.asset-cards .card-label { font-size: 13px; color: #909399; }
.asset-cards .card-value { font-size: 24px; font-weight: 700; margin: 4px 0; }
.asset-cards .card-sub { font-size: 12px; color: #909399; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
.section-card { margin-bottom: 0; }
.section-title { font-weight: 600; font-size: 15px; }
.risk-gauge { text-align: center; padding: 16px 0; }
.risk-level { font-size: 22px; font-weight: 700; padding: 12px; border-radius: 12px; }
.risk-level.level-1 { background: #e8f5e9; color: #27ae60; }
.risk-level.level-2 { background: #fff3e0; color: #e67e22; }
.risk-level.level-3 { background: #fdecea; color: #e74c3c; }
.risk-score { margin-top: 8px; color: #909399; font-size: 14px; }
.main-row { margin-top: 0; }
</style>
