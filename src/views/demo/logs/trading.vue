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
          <el-table-column prop="时间" label="时间" width="170" />
          <el-table-column prop="操作" label="操作" width="80">
            <template #default="{ row }">
              <el-tag :type="row['操作'] === '买入' ? 'success' : 'danger'" size="small">
                {{ row['操作'] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="代码" label="代码" width="110" />
          <el-table-column prop="名称" label="名称" width="100" />
          <el-table-column prop="数量" label="数量" width="80" align="right" />
          <el-table-column prop="价格" label="价格" width="90" align="right">
            <template #default="{ row }">
              <span v-if="row['价格'] === 0 || row['价格'] === '0'" class="text-muted">市价单</span>
              <span v-else>{{ row['价格'] }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="订单号" label="订单号" width="140" />
          <el-table-column prop="备注" label="备注" min-width="150" show-overflow-tooltip />
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
          <el-table-column prop="记录时间" label="记录时间" width="170" />
          <el-table-column prop="交易环境" label="环境" width="80">
            <template #default="{ row }">
              <el-tag :type="row['交易环境'] === 'REAL' ? 'danger' : 'info'" size="small">
                {{ row['交易环境'] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="操作" label="操作" width="70">
            <template #default="{ row }">
              <el-tag :type="row['操作'] === '买入' ? 'success' : 'danger'" size="small">
                {{ row['操作'] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="订单状态" label="状态" width="100">
            <template #default="{ row }">
              <el-tag
                :type="orderStatusTag(row['订单状态'])"
                size="small"
              >
                {{ row['订单状态'] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="订单号" label="订单号" width="140" />
          <el-table-column prop="代码" label="代码" width="110" />
          <el-table-column prop="名称" label="名称" width="100" />
          <el-table-column prop="订单数量" label="委托数量" width="85" align="right" />
          <el-table-column prop="订单价格" label="委托价" width="85" align="right" />
          <el-table-column prop="已成交数量" label="已成交" width="80" align="right" />
          <el-table-column prop="成交均价" label="成交均价" width="90" align="right" />
          <el-table-column prop="最后错误" label="错误信息" min-width="140" show-overflow-tooltip />
          <el-table-column prop="备注" label="备注" min-width="120" show-overflow-tooltip />
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
