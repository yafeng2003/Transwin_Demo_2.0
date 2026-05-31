<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>💹 交易日志</h2>
      <p class="page-desc">展示下单、撤单、成交等交易操作日志。</p>
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="fetchData">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="下单" name="order" />
        <el-tab-pane label="撤单" name="cancel" />
        <el-tab-pane label="成交" name="deal" />
      </el-tabs>

      <el-table :data="filteredList" stripe v-loading="loading" max-height="500">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="typeLabel" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === 'order' ? 'primary' : row.type === 'deal' ? 'success' : 'warning'" size="small">
              {{ row.typeLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="symbolCode" label="代码" width="100" />
        <el-table-column prop="symbolName" label="名称" width="100" />
        <el-table-column prop="message" label="日志内容" min-width="300" />
        <el-table-column prop="status" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="170" />
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
import { getTradingLogs } from '/@/api/demo/index'

defineOptions({ name: 'DemoLogsTrading' })

const loading = ref(false)
const list = ref<any[]>([])
const activeTab = ref('all')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const filteredList = computed(() =>
  activeTab.value === 'all' ? list.value : list.value.filter((i: any) => i.type === activeTab.value)
)

async function fetchData() {
  loading.value = true
  try {
    const res = await getTradingLogs({ page: page.value, size: size.value })
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
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
