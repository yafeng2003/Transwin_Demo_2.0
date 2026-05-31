<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>📋 风险事件中心</h2>
      <p class="page-desc">集中展示全部风险事件，支持按级别、状态筛选，查看事件详情与处理进度。</p>
    </div>

    <el-card>
      <!-- 筛选 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="事件级别">
          <el-select v-model="filterLevel" placeholder="全部" clearable style="width:120px" @change="fetchData">
            <el-option label="低" :value="1" /><el-option label="中" :value="2" /><el-option label="高" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width:120px" @change="fetchData">
            <el-option label="待处理" value="pending" /><el-option label="处理中" value="processing" />
            <el-option label="已解决" value="resolved" /><el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" stripe v-loading="loading" max-height="500">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="eventLabel" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.level >= 3 ? 'danger' : row.level === 2 ? 'warning' : 'info'" size="small">
              {{ row.eventLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="70">
          <template #default="{ row }">
            <el-tag :type="row.level >= 3 ? 'danger' : row.level === 2 ? 'warning' : 'info'" size="small">
              {{ ['', '低', '中', '高'][row.level] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="accountId" label="账户" width="100" />
        <el-table-column prop="message" label="事件描述" min-width="220" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="occurTime" label="发生时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template>
            <el-button text type="primary" size="small">详情</el-button>
            <el-button text type="success" size="small">处理</el-button>
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
import { onMounted, ref } from 'vue'
import { getRiskEvents } from '/@/api/demo/index'

defineOptions({ name: 'DemoRiskEvents' })

const loading = ref(false)
const list = ref<any[]>([])
const filterLevel = ref(null as any)
const filterStatus = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const statusMap: Record<string, string> = { pending: '待处理', processing: '处理中', resolved: '已解决', ignored: '已忽略' }
const statusTag = (s: string) => ({ pending: 'danger', processing: 'warning', resolved: 'success', ignored: 'info' }[s] || '')

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: page.value, size: size.value }
    if (filterLevel.value) params.level = filterLevel.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await getRiskEvents(params)
    list.value = res.data.list
    total.value = res.data.total
  } finally { loading.value = false }
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
