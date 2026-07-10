<template>
  <div class="demo-dashboard">
    <!-- ========== 策略总览（选定市场+账户+策略）========== -->
    <template v-if="demoStore.isStrategyOverview">
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
      <el-row :gutter="16" class="main-row pos-row">
        <!-- 左：持仓概览 -->
        <el-col :span="14">
          <el-card class="section-card">
            <template #header>
              <span class="section-title">持仓概览</span>
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
            <template #header><span class="section-title">持仓分布</span></template>
            <vab-chart :option="pieOption" class="demo-chart-md" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 第二行：风险状态 + 最近交易 -->
      <el-row :gutter="16" class="main-row" style="margin-top:16px">
        <!-- 风险状态 -->
        <el-col :span="24">
          <el-card class="section-card">
            <template #header>
              <span class="section-title">风险状态</span>
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
                </el-descriptions>
              </el-col>
            </el-row>
          </el-card>

          <!-- 最近交易 -->
          <el-card class="section-card" style="margin-top:16px">
            <template #header>
              <span class="section-title">最近交易动态</span>
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

    <!-- ========== 全市场总览 ========== -->
    <template v-else-if="demoStore.isAllMarkets">
      <!-- 各市场资产柱状图 -->
      <el-card class="section-card">
        <template #header>
          <span class="section-title">各市场资产对比</span>
        </template>
        <vab-chart v-if="allMarketAssets.length > 0" :option="assetBarOption" class="demo-chart-md" />
        <el-empty v-else description="暂无数据" />
      </el-card>

      <!-- 风控策略风险列表 -->
      <el-card class="section-card" style="margin-top:16px">
        <template #header>
          <span class="section-title">风险事件（全部策略）</span>
          <el-button text type="primary" style="float:right" @click="$router.push('/demo/risk/events')">
            风控详情 →
          </el-button>
        </template>
        <el-table :data="allRiskStrategies" stripe size="small" max-height="400">
          <el-table-column prop="marketName" label="市场" width="110" />
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
          <span class="section-title">最近交易动态（全部市场）</span>
          <el-button text type="primary" style="float:right" @click="$router.push('/demo/strategy/deals')">
            查看全部 →
          </el-button>
        </template>
        <el-table :data="recentDeals" stripe size="small" max-height="320">
          <el-table-column prop="marketName" label="市场" width="110" />
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

    <!-- ========== 市场总览（选定市场，未选账户）========== -->
    <template v-else-if="demoStore.isMarketOverview">
      <!-- 资产汇总卡片 -->
      <el-row :gutter="16" class="asset-cards">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">市场总资产</div>
            <div class="card-value">{{ formatMoney(marketOverviewAgg.totalAsset) }}</div>
            <div class="card-sub">{{ demoStore.currentMarketName }} · {{ marketOverviewAgg.accountCount }} 个账户</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">今日收益</div>
            <div class="card-value" :class="marketOverviewAgg.todayPnl >= 0 ? 'up' : 'down'">
              {{ formatMoney(marketOverviewAgg.todayPnl) }}
            </div>
            <div class="card-sub" :class="marketOverviewAgg.todayReturnRate >= 0 ? 'up' : 'down'">
              {{ formatRate(marketOverviewAgg.todayReturnRate) }}
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">持仓市值</div>
            <div class="card-value">{{ formatMoney(marketOverviewAgg.marketValue) }}</div>
            <div class="card-sub">现金 {{ formatMoney(marketOverviewAgg.cashBalance) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">累计收益</div>
            <div class="card-value" :class="marketOverviewAgg.totalPnl >= 0 ? 'up' : 'down'">
              {{ formatMoney(marketOverviewAgg.totalPnl) }}
            </div>
            <div class="card-sub" :class="marketOverviewAgg.totalReturnRate >= 0 ? 'up' : 'down'">
              {{ formatRate(marketOverviewAgg.totalReturnRate) }}
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 各账户资产对比 + 该市场风险 -->
      <el-row :gutter="16" class="main-row" style="margin-top:16px">
        <el-col :span="14">
          <el-card class="section-card">
            <template #header>
              <span class="section-title">各账户资产对比</span>
            </template>
            <vab-chart v-if="marketOverviewAccounts.length > 0" :option="marketAccountBarOption" class="demo-chart-md" />
            <el-empty v-else description="暂无账户数据" />
          </el-card>
        </el-col>
        <el-col :span="10">
          <el-card class="section-card">
            <template #header>
              <span class="section-title">市场风险状态</span>
              <el-button text type="primary" style="float:right" @click="$router.push('/demo/risk/overview')">
                风控详情 →
              </el-button>
            </template>
            <el-row :gutter="12">
              <el-col :span="10">
                <div class="risk-gauge">
                  <div class="risk-level" :class="'level-' + (marketOverviewRisk.riskLevel || 1)">
                    {{ ['低', '中', '高'][(marketOverviewRisk.riskLevel || 1) - 1] }}风险
                  </div>
                  <div class="risk-score">评分 {{ marketOverviewRisk.riskScore || '-' }}</div>
                </div>
              </el-col>
              <el-col :span="14">
                <el-descriptions :column="1" size="small" border>
                  <el-descriptions-item label="今日事件">{{ marketOverviewRisk.todayEvents ?? '-' }}</el-descriptions-item>
                  <el-descriptions-item label="待处理事件">{{ marketOverviewRisk.unresolvedEvents ?? '-' }}</el-descriptions-item>
                </el-descriptions>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近交易 -->
      <el-card class="section-card" style="margin-top:16px">
        <template #header>
          <span class="section-title">最近交易动态（{{ demoStore.currentMarketName }}）</span>
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
          <el-table-column prop="accountId" label="账户" width="90" />
        </el-table>
      </el-card>
    </template>

    <!-- ========== 账户总览（选定市场+账户，未选策略）========== -->
    <template v-else-if="demoStore.isAccountOverview">
      <!-- 资产概览卡片 -->
      <el-row :gutter="16" class="asset-cards">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">账户总资产</div>
            <div class="card-value">{{ formatMoney(accountOverviewAsset.totalAsset) }}</div>
            <div class="card-sub">净值 {{ accountOverviewAsset.netValue?.toFixed(4) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">今日收益</div>
            <div class="card-value" :class="accountOverviewAsset.todayPnl >= 0 ? 'up' : 'down'">
              {{ formatMoney(accountOverviewAsset.todayPnl) }}
            </div>
            <div class="card-sub" :class="accountOverviewAsset.todayReturnRate >= 0 ? 'up' : 'down'">
              {{ accountOverviewAsset.todayReturnRate >= 0 ? '+' : '' }}{{ accountOverviewAsset.todayReturnRate?.toFixed(2) }}%
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">持仓市值</div>
            <div class="card-value">{{ formatMoney(accountOverviewAsset.marketValue) }}</div>
            <div class="card-sub">现金 {{ formatMoney(accountOverviewAsset.cashBalance) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="card-label">累计收益</div>
            <div class="card-value" :class="accountOverviewAsset.totalPnl >= 0 ? 'up' : 'down'">
              {{ formatMoney(accountOverviewAsset.totalPnl) }}
            </div>
            <div class="card-sub" :class="accountOverviewAsset.totalReturnRate >= 0 ? 'up' : 'down'">
              {{ accountOverviewAsset.totalReturnRate >= 0 ? '+' : '' }}{{ accountOverviewAsset.totalReturnRate?.toFixed(2) }}%
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 各策略持仓对比 + 账户风险 -->
      <el-row :gutter="16" class="main-row" style="margin-top:16px">
        <el-col :span="14">
          <el-card class="section-card">
            <template #header>
              <span class="section-title">各策略持仓对比</span>
            </template>
            <el-table :data="accountOverviewStrategies" stripe size="small" max-height="320">
              <el-table-column prop="strategyId" label="策略" width="120" />
              <el-table-column prop="marketValue" label="持仓市值" width="120">
                <template #default="{ row }">{{ formatMoney(row.marketValue) }}</template>
              </el-table-column>
              <el-table-column prop="positionCount" label="持仓数" width="80" />
              <el-table-column prop="unrealizedPnl" label="浮动盈亏" width="120">
                <template #default="{ row }">
                  <span :class="row.unrealizedPnl >= 0 ? 'up' : 'down'">
                    {{ formatMoney(row.unrealizedPnl) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="dailyPnl" label="今日盈亏" width="120">
                <template #default="{ row }">
                  <span :class="row.dailyPnl >= 0 ? 'up' : 'down'">
                    {{ formatMoney(row.dailyPnl) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="10">
          <el-card class="section-card">
            <template #header>
              <span class="section-title">账户风险状态</span>
              <el-button text type="primary" style="float:right" @click="$router.push('/demo/risk/overview')">
                风控详情 →
              </el-button>
            </template>
            <el-row :gutter="12">
              <el-col :span="10">
                <div class="risk-gauge">
                  <div class="risk-level" :class="'level-' + (accountOverviewRisk.riskLevel || 1)">
                    {{ ['低', '中', '高'][(accountOverviewRisk.riskLevel || 1) - 1] }}风险
                  </div>
                  <div class="risk-score">评分 {{ accountOverviewRisk.riskScore || '-' }}</div>
                </div>
              </el-col>
              <el-col :span="14">
                <el-descriptions :column="1" size="small" border>
                  <el-descriptions-item label="今日事件">{{ accountOverviewRisk.todayEvents ?? '-' }}</el-descriptions-item>
                  <el-descriptions-item label="待处理事件">{{ accountOverviewRisk.unresolvedEvents ?? '-' }}</el-descriptions-item>
                  <el-descriptions-item label="最大回撤">{{ accountOverviewRisk.maxDrawdown != null ? accountOverviewRisk.maxDrawdown.toFixed(2) + '%' : '-' }}</el-descriptions-item>
                </el-descriptions>
              </el-col>
            </el-row>
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近交易 -->
      <el-card class="section-card" style="margin-top:16px">
        <template #header>
          <span class="section-title">最近交易动态（{{ demoStore.currentAccountLabel }}）</span>
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
    getAccounts,
    getAssetSummary,
    getPositionOverview,
    getRecentDeals,
    getRiskEvents,
    getRiskStatus,
} from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoDashboard' })

const demoStore = useDemoStore()

// ---------- 策略总览数据 ----------
const asset = ref<any>({})
const risk = ref<any>({})
const positions = ref<any[]>([])
const recentDeals = ref<any[]>([])
const allMarketAssets = ref<any[]>([])
const allRiskStrategies = ref<any[]>([])

// ---------- 市场总览数据 ----------
const marketOverviewAgg = ref<any>({ totalAsset: 0, todayPnl: 0, marketValue: 0, cashBalance: 0, totalPnl: 0, accountCount: 0 })
const marketOverviewAccounts = ref<any[]>([])
const marketOverviewRisk = ref<any>({})

// ---------- 账户总览数据 ----------
const accountOverviewAsset = ref<any>({})
const accountOverviewStrategies = ref<any[]>([])
const accountOverviewRisk = ref<any>({})

// ---------- 工具函数 ----------
const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
const formatRate = (v: number) => {
  if (v == null) return '-'
  return `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`
}

function statusTagType(s: string) {
  return s === 'pending' ? 'warning' : s === 'processing' ? 'info' : s === 'resolved' ? 'success' : ''
}
function statusLabel(s: string) {
  return ({ pending: '待处理', processing: '处理中', resolved: '已解决', ignored: '已忽略' } as any)[s] || s
}
function marketNameById(id: number) {
  return demoStore.markets.find((m: any) => m.id === id)?.name || `市场${id}`
}

// ---------- 策略总览：持仓饼图 ----------
const pieOption = computed(() => {
  const pieData = positions.value.map((p: any) => ({
    value: p.marketValue,
    name: p.symbolName || p.symbolCode,
  }))
  return {
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { bottom: 0, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
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

// ---------- 全市场总览：资产柱状图 ----------
const assetBarOption = computed(() => {
  if (allMarketAssets.value.length === 0) return {}
  const names = allMarketAssets.value.map((m: any) => m.name)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['总资产', '持仓市值', '现金余额'], bottom: 0, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
    grid: { left: 42, right: 28, bottom: 48, top: 28, containLabel: true },
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

// ---------- 市场总览：各账户资产柱状图 ----------
const marketAccountBarOption = computed(() => {
  if (marketOverviewAccounts.value.length === 0) return {}
  const names = marketOverviewAccounts.value.map((a: any) => a.label || a.accountId)
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['总资产', '持仓市值', '现金余额'], bottom: 0, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 12, color: '#526071' } },
    grid: { left: 42, right: 28, bottom: 48, top: 28, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => (v / 10000).toFixed(0) + '万' } },
    series: [
      {
        name: '总资产', type: 'bar',
        data: marketOverviewAccounts.value.map((a: any) => a.totalAsset || 0),
        itemStyle: { color: '#4e88f3', borderRadius: [4, 4, 0, 0] },
      },
      {
        name: '持仓市值', type: 'bar',
        data: marketOverviewAccounts.value.map((a: any) => a.marketValue || 0),
        itemStyle: { color: '#13ce66', borderRadius: [4, 4, 0, 0] },
      },
      {
        name: '现金余额', type: 'bar',
        data: marketOverviewAccounts.value.map((a: any) => a.cashBalance || 0),
        itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] },
      },
    ],
  }
})

// ==================== 数据刷新函数 ====================

/** 策略总览刷新（保持原有逻辑） */
async function refreshStrategyOverview() {
  const [aSumRes, posRes, rRes, dRes] = await Promise.all([
    getAssetSummary({ market_id: demoStore.marketId, account_id: demoStore.accountId }),
    getPositionOverview({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId }),
    getRiskStatus({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId }),
    getRecentDeals({ market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId, limit: 10 }),
  ])
  asset.value = aSumRes.data
  positions.value = posRes.data.positions
  risk.value = rRes.data
  recentDeals.value = dRes.data
}

/** 全市场总览刷新（保持原有逻辑） */
async function refreshAllMarkets() {
  const marketIds = demoStore.markets.map((m: any) => m.id)

  const accResults = await Promise.all(
    marketIds.map((id: number) => getAccounts({ market_id: id }))
  )
  const marketAccounts: Record<number, any[]> = {}
  marketIds.forEach((id: number, i: number) => {
    marketAccounts[id] = accResults[i]?.data || []
  })

  allMarketAssets.value = await Promise.all(marketIds.map(async (id: number, i: number) => {
    const m = demoStore.markets[i]
    const assets = await Promise.all(
      (marketAccounts[id] || []).map((acc: any) => getAssetSummary({ market_id: id, account_id: acc.id }).catch(() => ({ data: {} })))
    )
    const summary = assets.reduce((acc: any, item: any) => {
      const d = item.data || {}
      acc.totalAsset += d.totalAsset || 0
      acc.marketValue += d.marketValue || 0
      acc.cashBalance += d.cashBalance || 0
      return acc
    }, { totalAsset: 0, marketValue: 0, cashBalance: 0 })
    return { id, name: m?.name || '市场' + id, ...summary }
  }))

  // 风险事件：遍历所有市场，聚合每个市场第一个账户+策略的风险事件
  try {
    const allEvents: any[] = []
    for (const mktId of marketIds) {
      for (const acc of marketAccounts[mktId] || []) {
        for (const sid of acc.strategies || []) {
          try {
            const eventsRes = await getRiskEvents({ page: 1, size: 20, account_id: acc.id, strategy_id: sid })
            const list = eventsRes.data?.list || []
            allEvents.push(...list.map((row: any) => ({ ...row, marketId: mktId, marketName: marketNameById(mktId) })))
          } catch { /* skip this strategy */ }
        }
      }
    }
    allRiskStrategies.value = allEvents
  } catch {
    allRiskStrategies.value = []
  }

  // 最近交易：遍历所有市场聚合
  try {
    const allDeals: any[] = []
    for (const mktId of marketIds) {
      for (const acc of marketAccounts[mktId] || []) {
        for (const sid of acc.strategies || []) {
          try {
            const dealsRes = await getRecentDeals({ market_id: mktId, account_id: acc.id, strategy_id: sid, limit: 3 })
            const list = Array.isArray(dealsRes.data) ? dealsRes.data : []
            allDeals.push(...list.map((row: any) => ({ ...row, marketId: mktId, marketName: marketNameById(mktId) })))
          } catch { /* skip this strategy */ }
        }
      }
    }
    recentDeals.value = allDeals.slice(0, 20)
  } catch {
    recentDeals.value = []
  }
}

/** 市场总览刷新：汇总该市场下所有账户数据 */
async function refreshMarketOverview() {
  const mktId = demoStore.marketId
  let accList = demoStore.accounts
  try {
    const accRes = await getAccounts({ market_id: mktId })
    accList = accRes.data || []
    demoStore.accounts = accList
  } catch {
    accList = demoStore.accounts
  }

  if (accList.length === 0) {
    marketOverviewAgg.value = { totalAsset: 0, todayPnl: 0, marketValue: 0, cashBalance: 0, totalPnl: 0, accountCount: 0 }
    marketOverviewAccounts.value = []
    marketOverviewRisk.value = {}
    recentDeals.value = []
    return
  }

  // 并行获取所有账户的资产概览
  const assetResults = await Promise.all(
    accList.map((a: any) => getAssetSummary({ market_id: mktId, account_id: a.id }))
  )

  // 汇总 + 各账户列表
  let totalAsset = 0, todayPnl = 0, marketValue = 0, cashBalance = 0, totalPnl = 0
  const accountsData: any[] = []
  accList.forEach((a: any, i: number) => {
    const d = assetResults[i]?.data || {}
    totalAsset += d.totalAsset || 0
    todayPnl += d.todayPnl || 0
    marketValue += d.marketValue || 0
    cashBalance += d.cashBalance || 0
    totalPnl += d.totalPnl || 0
    accountsData.push({ accountId: a.id, label: a.label || a.name || a.id, ...d })
  })

  const todayReturnRate = totalAsset ? (todayPnl / totalAsset) * 100 : 0
  const totalReturnRate = totalAsset ? (totalPnl / totalAsset) * 100 : 0
  marketOverviewAgg.value = { totalAsset, todayPnl, todayReturnRate, marketValue, cashBalance, totalPnl, totalReturnRate, accountCount: accList.length }
  marketOverviewAccounts.value = accountsData

  // 市场风险：遍历所有账户+策略，取最高风险等级并汇总事件数
  try {
    let maxLevel = 1, maxScore = 0, totalToday = 0, totalUnresolved = 0
    for (const a of accList) {
      for (const sid of a.strategies || []) {
        try {
          const riskRes = await getRiskStatus({ market_id: mktId, account_id: a.id, strategy_id: sid })
          const d = riskRes.data
          if (d.riskLevel > maxLevel) maxLevel = d.riskLevel
          if (d.riskScore > maxScore) maxScore = d.riskScore
          totalToday += d.todayEvents || 0
          totalUnresolved += d.unresolvedEvents || 0
        } catch { /* skip this strategy */ }
      }
    }
    marketOverviewRisk.value = { riskLevel: maxLevel, riskScore: maxScore, todayEvents: totalToday, unresolvedEvents: totalUnresolved }
  } catch {
    marketOverviewRisk.value = {}
  }

  // 最近交易：遍历所有账户+策略聚合
  try {
    const allDeals: any[] = []
    for (const a of accList) {
      for (const sid of a.strategies || []) {
        try {
          const dealsRes = await getRecentDeals({ market_id: mktId, account_id: a.id, strategy_id: sid, limit: 3 })
          const list = Array.isArray(dealsRes.data) ? dealsRes.data : []
          allDeals.push(...list)
        } catch { /* skip this strategy */ }
      }
    }
    recentDeals.value = allDeals.slice(0, 20)
  } catch {
    recentDeals.value = []
  }
}

/** 账户总览刷新：汇总该账户下所有策略数据 */
async function refreshAccountOverview() {
  const mktId = demoStore.marketId
  const accId = demoStore.accountId
  const strats = demoStore.availableStrategies

  // 账户资产概览
  try {
    const aRes = await getAssetSummary({ market_id: mktId, account_id: accId })
    accountOverviewAsset.value = aRes.data
  } catch {
    accountOverviewAsset.value = {}
  }

  // 各策略持仓对比
  if (strats.length > 0) {
    try {
      const posResults = await Promise.all(
        strats.map((sid: string) => getPositionOverview({ market_id: mktId, account_id: accId, strategy_id: sid }))
      )
      accountOverviewStrategies.value = strats.map((sid: string, i: number) => {
        const d = posResults[i]?.data || {}
        const positions = d.positions || []
        const totalMV = positions.reduce((sum: number, p: any) => sum + (p.marketValue || 0), 0)
        const totalUPnl = positions.reduce((sum: number, p: any) => sum + (p.unrealizedPnl || 0), 0)
        return {
          strategyId: sid,
          marketValue: totalMV || d.totalMarketValue || 0,
          positionCount: positions.length,
          unrealizedPnl: totalUPnl,
          dailyPnl: d.todayPnl || 0,
        }
      })
    } catch {
      accountOverviewStrategies.value = []
    }
  } else {
    accountOverviewStrategies.value = []
  }

  // 账户风险状态：遍历所有策略聚合
  try {
    let maxLevel = 1, maxScore = 0, totalToday = 0, totalUnresolved = 0, worstDrawdown = 0
    for (const sid of strats) {
      try {
        const rRes = await getRiskStatus({ market_id: mktId, account_id: accId, strategy_id: sid })
        const d = rRes.data
        if (d.riskLevel > maxLevel) maxLevel = d.riskLevel
        if (d.riskScore > maxScore) maxScore = d.riskScore
        totalToday += d.todayEvents || 0
        totalUnresolved += d.unresolvedEvents || 0
        if (d.maxDrawdown != null && d.maxDrawdown < worstDrawdown) worstDrawdown = d.maxDrawdown
      } catch { /* skip this strategy */ }
    }
    accountOverviewRisk.value = { riskLevel: maxLevel, riskScore: maxScore, todayEvents: totalToday, unresolvedEvents: totalUnresolved, maxDrawdown: worstDrawdown }
  } catch {
    accountOverviewRisk.value = {}
  }

  // 最近交易：遍历所有策略聚合
  try {
    const allDeals: any[] = []
    for (const sid of strats) {
      try {
        const dealsRes = await getRecentDeals({ market_id: mktId, account_id: accId, strategy_id: sid, limit: 5 })
        const list = Array.isArray(dealsRes.data) ? dealsRes.data : []
        allDeals.push(...list)
      } catch { /* skip this strategy */ }
    }
    recentDeals.value = allDeals.slice(0, 20)
  } catch {
    recentDeals.value = []
  }
}

/** 根据当前模式分发到对应刷新函数 */
async function doRefresh() {
  if (demoStore.isAllMarkets) {
    await refreshAllMarkets()
  } else if (demoStore.isMarketOverview) {
    await refreshMarketOverview()
  } else if (demoStore.isAccountOverview) {
    await refreshAccountOverview()
  } else {
    await refreshStrategyOverview()
  }
}

watch(() => demoStore.switchVersion, doRefresh)
onMounted(doRefresh)
</script>

<style scoped>
.demo-dashboard { padding: 16px; }
.asset-cards {
  align-items: stretch;
  margin-bottom: 16px;
}
.asset-cards :deep(.el-col) {
  display: flex;
}
.asset-cards :deep(.el-card) {
  width: 100%;
}
.asset-cards :deep(.el-card__body) {
  display: flex;
  min-height: 112px;
  flex-direction: column;
  justify-content: center;
}
.asset-cards .card-label { font-size: 13px; color: #909399; }
.asset-cards .card-value { font-size: 24px; font-weight: 700; margin: 4px 0; }
.asset-cards .card-sub {
  min-height: 18px;
  font-size: 12px;
  color: #909399;
}
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
/* 持仓概览 / 持仓分布 这一行两卡片等高对齐 */
.pos-row :deep(.el-col) { display: flex; flex-direction: column; }
.pos-row .section-card { flex: 1; }
</style>
