<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>🖥 系统日志</h2>
      <p class="page-desc">展示系统运行日志、服务状态与异常记录。</p>
    </div>

    <el-card>
      <el-form :inline="true" class="filter-form">
        <el-form-item label="级别">
          <el-select v-model="filterLevel" placeholder="全部" clearable style="width:120px">
            <el-option label="INFO" value="INFO" /><el-option label="WARN" value="WARN" /><el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="filteredList" stripe v-loading="loading" max-height="550">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="level" label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.level === 'ERROR' ? 'danger' : row.level === 'WARN' ? 'warning' : 'info'" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="message" label="消息" min-width="280" />
        <el-table-column prop="createdAt" label="时间" width="170" />
        <el-table-column label="操作" width="80">
          <template><el-button text type="primary" size="small">详情</el-button></template>
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
import { computed, onMounted, ref } from 'vue'
import { getSystemLogs } from '/@/api/demo/index'

defineOptions({ name: 'DemoLogsSystem' })

const loading = ref(false)
const list = ref<any[]>([])
const filterLevel = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const filteredList = computed(() =>
  filterLevel.value ? list.value.filter((i: any) => i.level === filterLevel.value) : list.value
)

async function fetchData() {
  loading.value = true
  try {
    const res = await getSystemLogs({ page: page.value, size: size.value })
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
