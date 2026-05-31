<template>
  <div class="demo-page">
    <div class="page-header">
      <h2>✋ 人工干预</h2>
      <p class="page-desc">手动提交买入、卖出、改单操作，后端通过 is_manual 标记区分系统成交与人工成交。</p>
    </div>

    <el-row :gutter="16">
      <!-- 买入表单 -->
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">🟢 买入</span></template>
          <el-form :model="buyForm" label-width="80px" size="default">
            <el-form-item label="市场">
              <el-select v-model="buyForm.marketId" style="width:100%">
                <el-option label="沪深A股" :value="1" /><el-option label="港股" :value="2" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户">
              <el-select v-model="buyForm.accountId" style="width:100%">
                <el-option label="主账户" value="acc_main" /><el-option label="成长账户" value="acc_growth" />
              </el-select>
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="buyForm.symbolCode" placeholder="如 000001" />
            </el-form-item>
            <el-form-item label="价格类型">
              <el-radio-group v-model="buyForm.orderType">
                <el-radio :value="1">市价</el-radio>
                <el-radio :value="2">限价</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="价格" v-if="buyForm.orderType === 2">
              <el-input v-model="buyForm.price" placeholder="委托价格" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input v-model="buyForm.quantity" placeholder="委托数量（股）" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitBuy" :loading="submitting">提交买入</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 卖出表单 -->
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">🔴 卖出</span></template>
          <el-form :model="sellForm" label-width="80px" size="default">
            <el-form-item label="市场">
              <el-select v-model="sellForm.marketId" style="width:100%">
                <el-option label="沪深A股" :value="1" /><el-option label="港股" :value="2" />
              </el-select>
            </el-form-item>
            <el-form-item label="账户">
              <el-select v-model="sellForm.accountId" style="width:100%">
                <el-option label="主账户" value="acc_main" /><el-option label="成长账户" value="acc_growth" />
              </el-select>
            </el-form-item>
            <el-form-item label="股票代码">
              <el-input v-model="sellForm.symbolCode" placeholder="如 600519" />
            </el-form-item>
            <el-form-item label="价格类型">
              <el-radio-group v-model="sellForm.orderType">
                <el-radio :value="1">市价</el-radio>
                <el-radio :value="2">限价</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="价格" v-if="sellForm.orderType === 2">
              <el-input v-model="sellForm.price" placeholder="委托价格" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input v-model="sellForm.quantity" placeholder="委托数量（股），填0为全部" />
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="submitSell" :loading="submitting">提交卖出</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 改单表单 + 操作结果 -->
      <el-col :span="8">
        <el-card>
          <template #header><span class="section-title">🔄 改单</span></template>
          <el-form :model="modifyForm" label-width="80px" size="default">
            <el-form-item label="订单ID">
              <el-input v-model="modifyForm.orderId" placeholder="输入要修改的订单ID" />
            </el-form-item>
            <el-form-item label="新价格">
              <el-input v-model="modifyForm.price" placeholder="修改后的价格（留空不变）" />
            </el-form-item>
            <el-form-item label="新数量">
              <el-input v-model="modifyForm.quantity" placeholder="修改后的数量（留空不变）" />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="submitModify" :loading="submitting">提交修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 操作结果 -->
        <el-card v-if="lastResult" style="margin-top:16px" class="result-card">
          <template #header><span>📋 操作结果</span></template>
          <el-descriptions :column="1" size="small" border>
            <el-descriptions-item label="订单ID">{{ lastResult.orderId }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="lastResult.status === 'submitted' ? 'success' : 'warning'" size="small">
                {{ lastResult.status === 'submitted' ? '已提交' : lastResult.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="消息">{{ lastResult.message }}</el-descriptions-item>
            <el-descriptions-item label="时间">{{ lastResult.dealTime || lastResult.modifyTime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { manualBuy, manualModifyOrder, manualSell } from '/@/api/demo/index'

defineOptions({ name: 'DemoManual' })

const submitting = ref(false)
const lastResult = ref<any>(null)

const buyForm = reactive({ marketId: 1, accountId: 'acc_main', symbolCode: '', orderType: 1, price: '', quantity: '' })
const sellForm = reactive({ marketId: 1, accountId: 'acc_main', symbolCode: '', orderType: 1, price: '', quantity: '' })
const modifyForm = reactive({ orderId: '', price: '', quantity: '' })

async function submitBuy() {
  submitting.value = true
  try {
    const res = await manualBuy({ ...buyForm })
    lastResult.value = res.data
    ElMessage.success('买入委托已提交')
  } catch { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

async function submitSell() {
  submitting.value = true
  try {
    const res = await manualSell({ ...sellForm })
    lastResult.value = res.data
    ElMessage.success('卖出委托已提交')
  } catch { ElMessage.error('提交失败') }
  finally { submitting.value = false }
}

async function submitModify() {
  submitting.value = true
  try {
    const res = await manualModifyOrder({ ...modifyForm })
    lastResult.value = res.data
    ElMessage.success('订单修改成功')
  } catch { ElMessage.error('修改失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.demo-page { padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 20px; }
.page-desc { color: #909399; font-size: 13px; margin: 0; }
.section-title { font-weight: 600; font-size: 15px; }
.result-card { border: 1px solid #67C23A; }
</style>
