<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>系统日志</h2>
      <p class="page-desc">展示系统运行、交易执行、风控和策略模块日志。</p>
    </div>

    <el-card>
      <!-- 筛选栏 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="级别">
          <el-select v-model="filterLevel" placeholder="全部" clearable style="width:120px" @change="fetchData">
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="filterModule" placeholder="全部" clearable style="width:130px" @change="fetchData">
            <el-option label="系统" value="system" />
            <el-option label="交易执行" value="executor" />
            <el-option label="风控" value="risk" />
            <el-option label="策略" value="strategy" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键字">
          <el-input v-model="keyword" clearable placeholder="日志内容/详情" style="width:180px" @keyup.enter="fetchData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="filteredList" stripe v-loading="loading" max-height="500">
        <el-table-column prop="createdAt" label="时间" width="170" sortable />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="row.level === 'ERROR' ? 'danger' : row.level === 'WARNING' ? 'warning' : 'info'" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="message" label="日志内容" min-width="220" show-overflow-tooltip />
        <el-table-column prop="detail" label="详情" min-width="180" show-overflow-tooltip />
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
import { computed, onMounted, ref } from 'vue'
import { getSystemLogs } from '/@/api/demo/index'

defineOptions({ name: 'DemoLogsSystem' })

const loading = ref(false)
const list = ref<any[]>([])
const filterLevel = ref('')
const filterModule = ref('')
const keyword = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const filteredList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return list.value
  return list.value.filter((row: any) => `${row.message || ''} ${row.detail || ''}`.toLowerCase().includes(kw))
})

async function fetchData() {
  loading.value = true
  try {
    const res = await getSystemLogs({
      page: page.value,
      size: size.value,
      level: filterLevel.value || undefined,
      module: filterModule.value || undefined,
    })
    list.value = res.data.list
    total.value = res.data.total
  } finally { loading.value = false }
}

function resetFilters() {
  filterLevel.value = ''
  filterModule.value = ''
  keyword.value = ''
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
