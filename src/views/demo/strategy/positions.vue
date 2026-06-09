<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>持仓中心</h2>
      <p class="page-desc">展示当前持仓明细与盈亏，支持查看历史持仓记录。</p>
    </div>

    <!-- 持仓汇总 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">持仓标的数</div><div class="stat-value">{{ list.length }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">持仓总市值</div><div class="stat-value">{{ formatMoney(totalMarketValue) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">未实现盈亏</div><div class="stat-value" :class="totalUnrealizedPnl >= 0 ? 'up' : 'down'">{{ formatMoney(totalUnrealizedPnl) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">持仓策略数</div><div class="stat-value">{{ uniqueStrategies }}</div></el-card>
      </el-col>
    </el-row>

    <!-- 持仓表格 -->
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="当前持仓" name="current" />
        <el-tab-pane label="历史持仓" name="history" />
      </el-tabs>

      <el-table :data="list" stripe v-loading="loading" max-height="500">
        <el-table-column prop="symbolCode" label="代码" width="100" />
        <el-table-column prop="symbolName" label="名称" width="100" />
        <el-table-column prop="direction" label="方向" width="70">
          <template #default="{ row }">
            <el-tag :type="row.direction === 1 ? 'danger' : 'success'" size="small">
              {{ row.direction === 1 ? '多' : '空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="openPrice" label="开仓均价" width="100">
          <template #default="{ row }">{{ row.openPrice?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="currentPrice" label="现价" width="90">
          <template #default="{ row }">{{ row.currentPrice?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="holdingQuantity" label="持仓数量" width="90" />
        <el-table-column prop="holdingAmount" label="持仓金额" width="110">
          <template #default="{ row }">{{ formatMoney(row.holdingAmount) }}</template>
        </el-table-column>
        <el-table-column prop="unrealizedPnl" label="未实现盈亏" width="120">
          <template #default="{ row }">
            <span :class="row.unrealizedPnl >= 0 ? 'up' : 'down'">
              {{ formatMoney(row.unrealizedPnl) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="unrealizedPnlRate" label="盈亏比例" width="90">
          <template #default="{ row }">
            <span :class="row.unrealizedPnlRate >= 0 ? 'up' : 'down'">
              {{ row.unrealizedPnlRate >= 0 ? '+' : '' }}{{ row.unrealizedPnlRate?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="openTime" label="开仓时间" width="120" />
        <el-table-column prop="strategyId" label="策略" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue'
import { getCurrentPositions } from '/@/api/demo/index'

defineOptions({ name: 'DemoStrategyPositions' })

const loading = ref(false)
const list = ref<any[]>([])
const activeTab = ref('current')

const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const totalMarketValue = computed(() => list.value.reduce((s, i) => s + (i.holdingAmount || 0), 0))
const totalUnrealizedPnl = computed(() => list.value.reduce((s, i) => s + (i.unrealizedPnl || 0), 0))
const uniqueStrategies = computed(() => new Set(list.value.map((i: any) => i.strategyId)).size)

onMounted(async () => {
  loading.value = true
  try {
    const res = await getCurrentPositions()
    list.value = res.data
  } finally { loading.value = false }
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.stats-row { margin-bottom: 16px; }
.stat-label { font-size: 13px; color: #909399; }
.stat-value { font-size: 22px; font-weight: 700; margin-top: 4px; color: #303133; }
.up { color: #e74c3c; }
.down { color: #27ae60; }
</style>
