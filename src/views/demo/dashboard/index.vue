<template>
  <div class="demo-dashboard">
    <!-- ========== 单市场视图 ========== -->
    <template v-if="!isAllMarkets">
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
    </template>

    <!-- ========== 全市场总览视图 ========== -->
    <template v-else>
      <!-- 各市场资产柱状图 -->
      <el-card class="section-card">
        <template #header>
          <span class="section-title">📊 各市场资产对比</span>
        </template>
        <vab-chart v-if="allMarketAssets.length > 0" :option="assetBarOption" style="height:320px" />
        <el-empty v-else description="暂无数据" />
      </el-card>

      <!-- 风控策略风险列表 -->
      <el-card class="section-card" style="margin-top:16px">
        <template #header>
          <span class="section-title">🛡️ 风险事件（全部策略）</span>
          <el-button text type="primary" style="float:right" @click="$router.push('/demo/risk/events')">
            风控详情 →
          </el-button>
        </template>
        <el-table :data="allRiskStrategies" stripe size="small" max-height="400">
          <el-table-column prop="strategyId" label="策略" width="140" />
          <el-table-column prop="eventLabel" label="事件类型" width="130">
            <template #default="{ row }">
              <el-tag :type="row.level === 3 ? 'danger' : row.level === 2 ? 'warning' : 'info'" size="small">
                {{ row.eventLabel }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="级别" width="70">
            <template #default="{ row }">
              <el-tag :type="row.level === 3 ? 'danger' : row.level === 2 ? 'warning' : ''" size="small">
                {{ ['', '低', '中', '高'][row.level] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="accountId" label="账户" width="110" />
          <el-table-column prop="symbolCode" label="标的" width="90">
            <template #default="{ row }">{{ row.symbolCode || '-' }}</template>
          </el-table-column>
          <el-table-column prop="message" label="事件描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="occurTime" label="发生时间" width="170" />
        </el-table>
      </el-card>

      <!-- 最近交易 -->
      <el-card class="section-card" style="margin-top:16px">
        <template #header>
          <span class="section-title">📋 最近交易动态（全部市场）</span>
          <el-button text type="primary" style="float:right" @click="$router.push('/demo/strategy/deals')">
            查看全部 →
          </el-button>
        </template>
        <el-table :data="recentDeals" stripe size="small" max-height="320">
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
    </template>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
    getAssetSummary,
    getPositionOverview,
    getRecentDeals,
    getRiskEvents,
    getRiskStatus,
} from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoDashboard' })

const demoStore = useDemoStore()
const isAllMarkets = computed(() => demoStore.marketId === 0)
const asset = ref<any>({})
const risk = ref<any>({})
const positions = ref<any[]>([])
const recentDeals = ref<any[]>([])

// 全市场总览数据
const allMarketAssets = ref<any[]>([])
const allRiskStrategies = ref<any[]>([])

const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function statusTagType(s: string) {
  return s === 'pending' ? 'warning' : s === 'processing' ? 'info' : s === 'resolved' ? 'success' : ''
}
function statusLabel(s: string) {
  return ({ pending: '待处理', processing: '处理中', resolved: '已解决', ignored: '已忽略' } as any)[s] || s
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

// 全市场资产柱状图
const assetBarOption = computed(() => {
  if (allMarketAssets.value.length === 0) return {}
  const names = allMarketAssets.value.map((m: any) => m.name)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['总资产', '持仓市值', '现金余额'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => (v / 10000).toFixed(0) + '万' } },
    series: [
      {
        name: '总资产', type: 'bar',
        data: allMarketAssets.value.map((m: any) => m.totalAsset),
        itemStyle: { color: '#4e88f3', borderRadius: [4, 4, 0, 0] },
      },
      {
        name: '持仓市值', type: 'bar',
        data: allMarketAssets.value.map((m: any) => m.marketValue),
        itemStyle: { color: '#13ce66', borderRadius: [4, 4, 0, 0] },
      },
      {
        name: '现金余额', type: 'bar',
        data: allMarketAssets.value.map((m: any) => m.cashBalance),
        itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] },
      },
    ],
  }
})

async function refreshAll() {
  const [aSumRes, posRes, rRes, dRes] = await Promise.all([
    getAssetSummary({ market_id: demoStore.marketId, account_id: demoStore.accountId }),
    getPositionOverview({ market_id: demoStore.marketId, account_id: demoStore.accountId }),
    getRiskStatus({ market_id: demoStore.marketId, account_id: demoStore.accountId }),
    getRecentDeals({ market_id: demoStore.marketId, limit: 10 }),
  ])
  asset.value = aSumRes.data
  positions.value = posRes.data.positions
  risk.value = rRes.data
  recentDeals.value = dRes.data
}

async function refreshAllMarkets() {
  // 并行请求所有市场的资产数据
  const marketIds = demoStore.markets.map((m: any) => m.id)
  const assetResults = await Promise.all(
    marketIds.map((id: number) => getAssetSummary({ market_id: id, account_id: demoStore.accountId }))
  )
  allMarketAssets.value = marketIds.map((id: number, i: number) => {
    const m = demoStore.markets[i]
    return { id, name: m?.name || '市场' + id, ...assetResults[i].data }
  })

  // 请求风控事件（有风险的策略）
  try {
    const eventsRes = await getRiskEvents({ page: 1, size: 100 })
    allRiskStrategies.value = eventsRes.data.list || []
  } catch {
    allRiskStrategies.value = []
  }

  // 跨市场交易动态
  try {
    const dealsRes = await getRecentDeals({ limit: 10 })
    recentDeals.value = dealsRes.data
  } catch {
    recentDeals.value = []
  }
}

async function doRefresh() {
  if (isAllMarkets.value) {
    await refreshAllMarkets()
  } else {
    await refreshAll()
  }
}

watch(() => demoStore.marketId, doRefresh)
onMounted(doRefresh)
</script>

<style scoped>
.demo-dashboard { padding: 16px; }
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
