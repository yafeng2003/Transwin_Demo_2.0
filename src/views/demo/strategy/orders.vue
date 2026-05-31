<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>📋 订单中心</h2>
      <p class="page-desc">展示策略生成的委托订单，包括待执行、已成交、失败等各状态订单。</p>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filter" size="default">
        <el-form-item label="市场">
          <el-select v-model="filter.marketId" placeholder="全部" clearable style="width:120px">
            <el-option label="沪深A股" :value="1" />
            <el-option label="港股" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="账户">
          <el-select v-model="filter.accountId" placeholder="全部" clearable style="width:130px">
            <el-option v-for="a in accounts" :key="a.id" :label="a.label" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filter.status" placeholder="全部" clearable style="width:120px">
            <el-option label="待执行" :value="0" />
            <el-option label="已成交" :value="1" />
            <el-option label="失败" :value="2" />
            <el-option label="部分成交" :value="3" />
            <el-option label="已撤销" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="标的">
          <el-input v-model="filter.symbol" placeholder="代码/名称" clearable style="width:140px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单表格 -->
    <el-card>
      <el-table :data="list" stripe v-loading="loading" max-height="550">
        <el-table-column prop="id" label="订单ID" width="90" />
        <el-table-column prop="symbolCode" label="标的代码" width="100" />
        <el-table-column prop="symbolName" label="标的名称" width="100" />
        <el-table-column prop="operationType" label="开/平" width="70">
          <template #default="{ row }">{{ row.operationType === 1 ? '开仓' : '平仓' }}</template>
        </el-table-column>
        <el-table-column prop="direction" label="方向" width="70">
          <template #default="{ row }">
            <el-tag :type="row.direction === 1 ? 'danger' : 'success'" size="small">
              {{ row.direction === 1 ? '多' : '空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="orderType" label="类型" width="70">
          <template #default="{ row }">{{ row.orderType === 1 ? '市价' : '限价' }}</template>
        </el-table-column>
        <el-table-column prop="price" label="委托价" width="90">
          <template #default="{ row }">{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.statusLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="strategyId" label="策略" width="120" />
        <el-table-column prop="createdAt" label="生成时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default>
            <el-button text type="primary" size="small">详情</el-button>
            <el-button text type="warning" size="small">撤单</el-button>
          </template>
        </el-table-column>
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
import { onMounted, reactive, ref } from 'vue'
import { getAccounts, getOrders } from '/@/api/demo/index'

defineOptions({ name: 'DemoStrategyOrders' })

const loading = ref(false)
const list = ref<any[]>([])
const accounts = ref<any[]>([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const filter = reactive({ marketId: null as any, accountId: '', status: null as any, symbol: '' })

const statusType = (s: number) => {
  const map: Record<number, string> = { 0: 'info', 1: 'success', 2: 'danger', 3: 'warning', 4: '' }
  return map[s] || ''
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: page.value, size: size.value }
    if (filter.marketId != null) params.market_id = filter.marketId
    if (filter.accountId) params.account_id = filter.accountId
    if (filter.status != null) params.status = filter.status
    if (filter.symbol) params.symbol = filter.symbol
    const res = await getOrders(params)
    list.value = res.data.list
    total.value = res.data.total
  } finally { loading.value = false }
}

function resetFilter() {
  filter.marketId = null; filter.accountId = ''; filter.status = null; filter.symbol = ''
  page.value = 1
  fetchData()
}

onMounted(async () => {
  const aRes = await getAccounts()
  accounts.value = aRes.data
  fetchData()
})
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.filter-card { margin-bottom: 16px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
