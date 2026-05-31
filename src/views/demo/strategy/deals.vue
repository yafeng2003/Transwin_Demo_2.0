<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>💱 成交中心</h2>
      <p class="page-desc">展示策略实际执行的成交记录，包含实时成交与历史成交。</p>
    </div>

    <!-- 成交统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">今日成交笔数</div><div class="stat-value">{{ stats.todayCount }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">今日成交金额</div><div class="stat-value">{{ formatMoney(stats.todayAmount) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">今日手续费</div><div class="stat-value">{{ formatMoney(stats.todayCommission) }}</div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover"><div class="stat-label">本月成交笔数</div><div class="stat-value">{{ stats.monthCount }}</div></el-card>
      </el-col>
    </el-row>

    <!-- Tab 切换：实时 / 历史 -->
    <el-card>
      <el-tabs v-model="activeTab" @tab-change="fetchData">
        <el-tab-pane label="历史成交" name="history" />
        <el-tab-pane label="实时成交" name="realtime" />
      </el-tabs>

      <el-table :data="list" stripe v-loading="loading" max-height="500">
        <el-table-column prop="id" label="成交ID" width="90" />
        <el-table-column prop="symbolCode" label="代码" width="100" />
        <el-table-column prop="symbolName" label="名称" width="100" />
        <el-table-column prop="dealType" label="开/平" width="70">
          <template #default="{ row }">{{ row.dealType === 1 ? '开仓' : '平仓' }}</template>
        </el-table-column>
        <el-table-column prop="direction" label="方向" width="70">
          <template #default="{ row }">
            <el-tag :type="row.direction === 1 ? 'danger' : 'success'" size="small">
              {{ row.direction === 1 ? '多' : '空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dealPrice" label="成交价" width="90">
          <template #default="{ row }">{{ row.dealPrice?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="dealQuantity" label="数量" width="80" />
        <el-table-column prop="dealAmount" label="成交金额" width="110">
          <template #default="{ row }">{{ formatMoney(row.dealAmount) }}</template>
        </el-table-column>
        <el-table-column prop="commission" label="手续费" width="80">
          <template #default="{ row }">{{ row.commission?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="isManual" label="来源" width="70">
          <template #default="{ row }">
            <el-tag :type="row.isManual ? 'warning' : ''" size="small">
              {{ row.isManual ? '人工' : '系统' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="strategyId" label="策略" width="120" />
        <el-table-column prop="dealTime" label="成交时间" width="170" />
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page" v-model:page-size="size"
          :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
          @size-change="fetchData" @current-change="fetchData" />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getDeals, getDealStats } from '/@/api/demo/index'

defineOptions({ name: 'DemoStrategyDeals' })

const loading = ref(false)
const list = ref<any[]>([])
const stats = ref<any>({})
const activeTab = ref('history')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const formatMoney = (v: number) => {
  if (v == null) return '-'
  return (v >= 0 ? '¥' : '-¥') + Math.abs(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function fetchData() {
  loading.value = true
  try {
    const [dRes, sRes] = await Promise.all([
      getDeals({ page: page.value, size: size.value }),
      getDealStats(),
    ])
    list.value = dRes.data.list
    total.value = dRes.data.total
    stats.value = sRes.data
  } finally { loading.value = false }
}

onMounted(fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.stats-row { margin-bottom: 16px; }
.stat-label { font-size: 13px; color: #909399; }
.stat-value { font-size: 22px; font-weight: 700; margin-top: 4px; color: #303133; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
