<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>执行风险监控</h2>
      <p class="page-desc">监控交易执行过程中的下单失败、撤单失败、API异常与超时事件。</p>
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="全部事件" name="all" />
        <el-tab-pane v-for="t in eventTypes" :key="t.value" :label="t.label" :name="t.value" />
      </el-tabs>

      <el-table :data="filteredList" stripe v-loading="loading" max-height="500">
        <el-table-column prop="id" label="事件ID" width="90" />
        <el-table-column prop="eventLabel" label="事件类型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.level >= 3 ? 'danger' : row.level >= 2 ? 'warning' : ''" size="small">
              {{ row.eventLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="70">
          <template #default="{ row }">
            <el-tag :type="row.level >= 3 ? 'danger' : row.level >= 2 ? 'warning' : 'info'" size="small">
              {{ ['', '低', '中', '高'][row.level] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="accountId" label="账户" width="110" />
        <el-table-column prop="strategyId" label="策略" width="130" />
        <el-table-column prop="symbolCode" label="标的" width="90" />
        <el-table-column prop="message" label="事件描述" min-width="200" />
        <el-table-column prop="status" label="处理状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="occurTime" label="发生时间" width="170" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              text type="primary" size="small"
              :loading="row._resolving"
              @click="handleResolve(row)"
            >处理</el-button>
            <span v-else-if="row.status === 'resolved'" style="color:#67c23a;font-size:13px">已处理</span>
            <span v-else style="color:#909399;font-size:13px">--</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page" v-model:page-size="size"
          :total="displayTotal" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
          @size-change="fetchData" @current-change="fetchData" />
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { getRiskEvents, resolveRiskEvent } from '/@/api/demo/index'
import { useDemoStore } from '/@/store/modules/demo'

defineOptions({ name: 'DemoRiskExecution' })

const demoStore = useDemoStore()
const loading = ref(false)
const list = ref<any[]>([])
const activeTab = ref('all')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const EVENT_LABELS: Record<string, string> = {
  api_error: 'API异常', api_timeout: 'API超时', timeout: '超时异常',
  order_delay: '下单延迟', modify_failed: '改单失败',
  slippage_warning: '滑点预警', daily_loss: '日亏损超限',
  drawdown: '回撤超限', consecutive_loss: '连续亏损',
}

const eventTypes = computed(() => {
  const seen = new Set<string>()
  return list.value
    .map(i => i.eventType)
    .filter(t => { if (seen.has(t)) return false; seen.add(t); return true })
    .map(t => ({ value: t, label: EVENT_LABELS[t] || t }))
})

const filteredList = computed(() => {
  const filtered = activeTab.value === 'all'
    ? list.value
    : list.value.filter((i: any) => i.eventType === activeTab.value)
  return filtered
})

const displayTotal = computed(() => filteredList.value.length)

function onTabChange() { /* tab 切换时 filteredList 自动重新计算 */ }

const statusLabel = (s: string) => ({ pending: '待处理', processing: '处理中', resolved: '已处理', ignored: '已忽略' }[s] || s)
const statusTagType = (s: string) => ({ pending: 'danger', processing: 'warning', resolved: 'success', ignored: 'info' }[s] || '')

async function handleResolve(row: any) {
  try {
    await ElMessageBox.confirm(
      `确认处理事件 #${row.id}（${row.eventLabel}）？处理后状态将变更为「已处理」。`,
      '处理确认',
      { confirmButtonText: '确认处理', cancelButtonText: '取消', type: 'warning' }
    )
    row._resolving = true
    await resolveRiskEvent({ id: row.id })
    row.status = 'resolved'
    ElMessage.success(`事件 #${row.id} 已处理`)
  } catch (err: any) {
    if (err !== 'cancel' && err?.message !== 'cancel') {
      ElMessage.error(err?.message || '处理失败')
    }
  } finally {
    row._resolving = false
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await getRiskEvents({ page: page.value, size: 100, market_id: demoStore.marketId, account_id: demoStore.accountId, strategy_id: demoStore.strategyId })
    list.value = res.data.list
    total.value = res.data.total
  } finally { loading.value = false }
}

onMounted(fetchData)
watch(() => demoStore.switchVersion, () => { page.value = 1; fetchData() })
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
