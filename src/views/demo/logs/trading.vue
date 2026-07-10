<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>交易日志</h2>
      <p class="page-desc">展示下单日志与订单状态回调日志，对应后端 trade_log / order_log。</p>
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="fetchData">
        <el-tab-pane label="下单日志" name="trade" />
        <el-tab-pane label="订单状态" name="order" />
      </el-tabs>

      <!-- ========== 下单日志 (trade_log) ========== -->
      <template v-if="activeTab === 'trade'">
        <el-table :data="tradeList" stripe v-loading="tradeLoading" max-height="500">
          <el-table-column prop="createdAt" label="时间" width="170" sortable />
          <el-table-column prop="typeLabel" label="操作" width="80">
            <template #default="{ row }">
              <el-tag :type="row.type === 'deal' ? 'success' : row.type === 'cancel' ? 'warning' : 'info'" size="small">
                {{ row.typeLabel }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="symbolCode" label="代码" width="110" sortable />
          <el-table-column prop="symbolName" label="名称" width="120" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="message" label="日志内容" min-width="260" show-overflow-tooltip />
        </el-table>

        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="tradePage" v-model:page-size="tradeSize"
            :total="tradeTotal" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
            @size-change="fetchTradeLogs" @current-change="fetchTradeLogs" />
        </div>
      </template>

      <!-- ========== 订单状态日志 (order_log) ========== -->
      <template v-if="activeTab === 'order'">
        <el-table :data="orderList" stripe v-loading="orderLoading" max-height="500">
          <el-table-column prop="createdAt" label="记录时间" width="170" sortable />
          <el-table-column prop="typeLabel" label="类型" width="90">
            <template #default="{ row }">
              <el-tag :type="row.type === 'order' ? 'info' : 'warning'" size="small">
                {{ row.typeLabel }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="orderStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="symbolCode" label="代码" width="110" sortable />
          <el-table-column prop="symbolName" label="名称" width="120" />
          <el-table-column prop="message" label="日志内容" min-width="260" show-overflow-tooltip />
        </el-table>

        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="orderPage" v-model:page-size="orderSize"
            :total="orderTotal" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
            @size-change="fetchOrderLogs" @current-change="fetchOrderLogs" />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getOrderLogs, getTradeLogs } from '/@/api/demo/index'

defineOptions({ name: 'DemoLogsTrading' })

const activeTab = ref('trade')

// ---- 下单日志 ----
const tradeLoading = ref(false)
const tradeList = ref<any[]>([])
const tradePage = ref(1)
const tradeSize = ref(20)
const tradeTotal = ref(0)

async function fetchTradeLogs() {
  tradeLoading.value = true
  try {
    const res = await getTradeLogs({ page: tradePage.value, size: tradeSize.value })
    tradeList.value = res.data.list
    tradeTotal.value = res.data.total
  } finally { tradeLoading.value = false }
}

// ---- 订单状态日志 ----
const orderLoading = ref(false)
const orderList = ref<any[]>([])
const orderPage = ref(1)
const orderSize = ref(20)
const orderTotal = ref(0)

async function fetchOrderLogs() {
  orderLoading.value = true
  try {
    const res = await getOrderLogs({ page: orderPage.value, size: orderSize.value })
    orderList.value = res.data.list
    orderTotal.value = res.data.total
  } finally { orderLoading.value = false }
}

function orderStatusTag(status: string) {
  const map: Record<string, string> = {
    SUBMITTED: 'info',
    FILLED_ALL: 'success',
    FILLED_PART: 'warning',
    FAILED: 'danger',
    DISABLED: 'danger',
    DELETED: 'info',
    CANCELLED_ALL: 'info',
    CANCELLED_PART: 'warning',
  }
  return map[status] || 'info'
}

function fetchData() {
  if (activeTab.value === 'trade') fetchTradeLogs()
  else fetchOrderLogs()
}

onMounted(fetchTradeLogs)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
.text-muted { color: #909399; font-style: italic; }
</style>
