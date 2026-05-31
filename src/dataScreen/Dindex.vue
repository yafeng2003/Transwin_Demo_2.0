<template>
  <div id="data-screen-container" class="data-screen-container vab-data-fullscreen">
    <div>
      <data-screen-header
        :style="{
          height: headerContentHeight,
          'line-height': headerContentHeight,
        }"
      />
      <div style="padding: 30px 40px 0 40px">
        <el-row :gutter="20">
          <el-col :span="6" :xs="24">
            <div class="data-screen-card" :style="{ height: leftCardHeight1 }">
              <div class="card-title">热点事件检测</div>
              <data-screen-left1 />
            </div>
            <div class="data-screen-card" :style="{ height: leftCardHeight2 }">
              <div class="card-title">主题挖掘</div>
              <data-screen-left2 />
            </div>
            <div class="data-screen-card" :style="{ height: leftCardHeight3 }">
              <div class="card-title">品牌健康监测</div>
              <data-screen-left3 />
            </div>
          </el-col>
          <el-col :span="12" :xs="24">
            <div class="data-screen-card mid-card" :style="{ height: topCardHeight }">
              <data-screen-mid />
            </div>
            <div class="data-screen-card hidden-xs-only" :style="{ height: bottomCardHeight }">
              <data-screen-bottom />
            </div>
            <div class="" :style="{ height: unitCardHeight }">
              <data-screen-unit />
            </div>
          </el-col>
          <el-col :span="6" :xs="24">
            <div class="data-screen-card" :style="{ height: rightCardHeight1 }">
              <div class="card-title">主题热度变迁</div>
              <data-screen-right1 />
            </div>
            <div class="data-screen-card" :style="{ height: rightCardHeight2 }">
              <div class="card-title">市场趋势预测</div>
              <data-screen-right2 />
            </div>
            <div class="data-screen-card" :style="{ height: rightCardHeight3 }">
              <div class="card-title">投资建议生成</div>
              <data-screen-right3 />
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
    <!-- <vab-theme-setting /> -->
  </div>
</template>

<script lang="ts" setup>
import dataScreenBottom from './components/DataScreenBottom.vue'
import dataScreenHeader from './components/DataScreenHeader.vue'
import dataScreenLeft1 from './components/DataScreenLeft1.vue'
import dataScreenLeft2 from './components/DataScreenLeft2.vue'
import dataScreenLeft3 from './components/DataScreenLeft3.vue'
import dataScreenMid from './components/dataScreenMid.vue'
import dataScreenRight1 from './components/DataScreenRight1.vue'
import dataScreenRight2 from './components/DataScreenRight2.vue'
import dataScreenRight3 from './components/DataScreenRight3.vue'
import dataScreenUnit from './components/DataScreenUnit.vue'

defineOptions({
  name: 'DataScreen',
})

const headerContentHeight = ref<any>('60px')
const topCardHeight = ref<any>('calc((var(--vh, 1vh) * 100 - 360px)')
const bottomCardHeight = ref<any>('150px')
const unitCardHeight = ref<any>('20px')

const leftCardHeight1 = ref<any>('calc((var(--vh, 1vh) * 100 - 165px) / 3.5)')
const leftCardHeight2 = ref<any>('calc((var(--vh, 1vh) * 100 - 165px) / 3)')
const leftCardHeight3 = ref<any>('calc((var(--vh, 1vh) * 100 - 165px) / 2.63)')

const rightCardHeight1 = ref<any>('calc((var(--vh, 1vh) * 100 - 165px) / 3)')
const rightCardHeight2 = ref<any>('calc((var(--vh, 1vh) * 100 - 165px) / 2.63)')
const rightCardHeight3 = ref<any>('calc((var(--vh, 1vh) * 100 - 165px) / 3.5)')

onMounted(() => {
  // setTimeout(() => {
  //   $baseMessage('点击右上角【全屏】按钮使用效果更佳', 'success', 'hey')
  // }, 1000)
  document.querySelectorAll('body')[0].className = ''

  if (location.hostname.includes('vuejs-core')) {
    // 数据大屏占用内存较大，演示地址每隔15分钟刷新一次页面缓解浏览器压力
    setTimeout(
      () => {
        //@ts-ignore
        location.reload(true)
      },
      1000 * 60 * 15
    )
  }
})
</script>

<style lang="scss" scoped>
#data-screen-container.data-screen-container.vab-data-fullscreen {
  overflow: auto;
  color: #fff;
  background: #01022e !important;

  :deep() {
    .vab-theme-setting {
      background: #01022e;
      border: 1px solid #101f58;

      section {
        > div {
          &:nth-child(1),
          &:nth-child(2),
          &:nth-child(3),
          &:nth-child(4) {
            display: none;
          }
        }
      }
    }
  }

  .data-screen-card {
    position: relative;
    width: 100%;
    min-height: 160px;
    padding: var(--el-padding);
    margin-bottom: 20px;
    border: 3px solid #01ffff;
    border-radius: 5px;

    .card-title {
      height: 20px;
      padding-left: 10px;
      font-size: 1.2rem;
      // font-weight: 600;
      line-height: 20px;
      text-align: left;
      border-left: 3px solid #01ffff;
    }

    &::before {
      position: absolute;
      top: -3px;
      bottom: -3px;
      left: 30px;
      z-index: 0;
      width: calc(100% - 60px);
      pointer-events: none;
      content: '';
      border-top: 3px solid #101f58;
      border-bottom: 3px solid #101f58;
    }

    &::after {
      position: absolute;
      top: 30px;
      right: -3px;
      left: -3px;
      z-index: 0;
      height: calc(100% - 60px);
      pointer-events: none;
      content: '';
      border-right: 3px solid #101f58;
      border-left: 3px solid #101f58;
    }
  }
  .mid-card {
    padding: 1px;
  }
}
</style>
