<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>⚠️ 错误日志</h2>
      <p class="page-desc">展示系统运行中的错误记录，对应后端 error_log。错误类型含固定枚举与订单状态类动态值。</p>
    </div>

    <el-card>
      <!-- 筛选栏 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="阶段">
          <el-select v-model="filterStage" placeholder="全部" clearable style="width:130px" @change="fetchData">
            <el-option label="交易执行" value="executor" />
            <el-option label="风控检查" value="risk" />
            <el-option label="策略调度" value="strategy" />
            <el-option label="订单回调" value="callback" />
            <el-option label="清理阶段" value="cleanup" />
          </el-select>
        </el-form-item>
        <el-form-item label="动作">
          <el-select v-model="filterAction" placeholder="全部" clearable style="width:130px" @change="fetchData">
            <el-option label="买入" value="BUY" />
            <el-option label="卖出" value="SELL" />
            <el-option label="持仓检查" value="POSITION" />
            <el-option label="解锁交易" value="unlock_trade" />
            <el-option label="订单更新" value="order_update" />
            <el-option label="清理" value="cleanup" />
          </el-select>
        </el-form-item>
        <el-form-item label="错误类型">
          <el-select v-model="filterErrorType" placeholder="全部" clearable style="width:180px" @change="fetchData">
            <el-option
              v-for="et in errorTypeOptions"
              :key="et"
              :label="et"
              :value="et"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" stripe v-loading="loading" max-height="500">
        <el-table-column prop="时间" label="时间" width="170" />
        <el-table-column prop="阶段" label="阶段" width="100" />
        <el-table-column prop="代码" label="代码" width="110" />
        <el-table-column prop="动作" label="动作" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row['动作'] === 'BUY' ? 'success' : row['动作'] === 'SELL' ? 'danger' : 'info'"
              size="small"
            >
              {{ row['动作'] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="错误类型" label="错误类型" width="160">
          <template #default="{ row }">
            <el-tag
              :type="isDynamicErrorType(row['错误类型']) ? 'warning' : 'danger'"
              size="small"
            >
              {{ row['错误类型'] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="错误详情" label="错误详情" min-width="220" show-overflow-tooltip />
        <el-table-column prop="订单号" label="订单号" width="140" />
        <el-table-column prop="备注" label="备注" min-width="120" show-overflow-tooltip />
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
import { getErrorLogs } from '/@/api/demo/index'

defineOptions({ name: 'DemoLogsSystem' })

// 固定错误枚举
const FIXED_ERROR_TYPES = [
  'unlock_failed',
  'invalid_weight',
  'account_assets_unavailable',
  'price_unavailable',
  'insufficient_cash',
  'callback_failed',
  'callback_exception',
  'qty_below_lot',
  'max_buy_query_failed',
  'max_buy_zero',
  'place_order_failed',
  'no_position',
  'fill_callback_exception',
  'position_query_failed',
  'buy_not_in_actual_position',
  'position_not_in_actual_position',
  'unhandled_exception',
]

// 订单状态类动态 error_type
const DYNAMIC_ERROR_TYPES = ['FAILED', 'DISABLED', 'DELETED']

const errorTypeOptions = [...FIXED_ERROR_TYPES, ...DYNAMIC_ERROR_TYPES]

function isDynamicErrorType(type: string) {
  return DYNAMIC_ERROR_TYPES.includes(type)
}

const loading = ref(false)
const list = ref<any[]>([])
const filterStage = ref('')
const filterAction = ref('')
const filterErrorType = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)

async function fetchData() {
  loading.value = true
  try {
    const res = await getErrorLogs({
      page: page.value,
      size: size.value,
      stage: filterStage.value || undefined,
      action: filterAction.value || undefined,
      errorType: filterErrorType.value || undefined,
    })
    list.value = res.data.list
    total.value = res.data.total
  } finally { loading.value = false }
}

function resetFilters() {
  filterStage.value = ''
  filterAction.value = ''
  filterErrorType.value = ''
  page.value = 1
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.filter-form { margin-bottom: 0; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
