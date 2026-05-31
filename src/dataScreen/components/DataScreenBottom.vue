<template>
  <el-row class="data-screen-bottom">
    <el-col :span="6">
      <el-row>
        <el-col :span="12">
          <el-image class="data-screen-bottom-icon" :src="bottom_01" />
        </el-col>
        <el-col :span="12">
          <div class="data-screen-bottom-text">
            <vab-count :end-value="countConfig1.endValue" :start-value="countConfig1.startValue" />
            <p>总体数据</p>
          </div>
        </el-col>
      </el-row>
    </el-col>
    <el-col :span="6">
      <el-row>
        <el-col :span="12">
          <el-image class="data-screen-bottom-icon" :src="bottom_02" />
        </el-col>
        <el-col :span="12">
          <div class="data-screen-bottom-text">
            <vab-count :end-value="countConfig2.endValue" :start-value="countConfig2.startValue" />
            <p>新闻数据</p>
          </div>
        </el-col>
      </el-row>
    </el-col>
    <el-col :span="6">
      <el-row>
        <el-col :span="12">
          <el-image class="data-screen-bottom-icon" :src="bottom_03" />
        </el-col>
        <el-col :span="12">
          <div class="data-screen-bottom-text">
            <vab-count :end-value="countConfig3.endValue" :start-value="countConfig3.startValue" />
            <p>媒体数据</p>
          </div>
        </el-col>
      </el-row>
    </el-col>
    <el-col :span="6">
      <el-row>
        <el-col :span="12">
          <el-image class="data-screen-bottom-icon" :src="bottom_04" />
        </el-col>
        <el-col :span="12">
          <div class="data-screen-bottom-text">
            <vab-count :end-value="countConfig4.endValue" :start-value="countConfig4.startValue" />
            <p>投资事件</p>
          </div>
        </el-col>
      </el-row>
    </el-col>
  </el-row>
</template>

<script lang="ts" setup>
import { random } from 'lodash-es'
import bottom_01 from '/@/assets/data_screen_images/bottom_01.png'
import bottom_02 from '/@/assets/data_screen_images/bottom_02.png'
import bottom_03 from '/@/assets/data_screen_images/bottom_03.png'
import bottom_04 from '/@/assets/data_screen_images/bottom_04.png'

defineOptions({
  name: 'DataScreenBottom',
})

const countConfig1 = reactive({
  startValue: 0,
  endValue: random(8000000, 9000000),
})

const countConfig2 = reactive({
  startValue: 0,
  endValue: random(400000, 500000),
})

const countConfig3 = reactive({
  startValue: 0,
  endValue: random(200000, 300000),
})

const countConfig4 = reactive({
  startValue: 0,
  endValue: random(300000, 400000),
})

const timer = setInterval(() => {
  countConfig1.endValue = countConfig1.endValue + random(0, 100)
  countConfig2.endValue = countConfig2.endValue + random(0, 100)
  countConfig3.endValue = countConfig3.endValue + random(0, 100)
  countConfig4.endValue = countConfig4.endValue + random(0, 100)
}, 1000 * 5)

onBeforeUnmount(() => {
  clearInterval(timer)
})
</script>

<style lang="scss" scoped>
.data-screen-bottom {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;

  .data-screen-bottom-text p {
    font-size: 1rem;
  }
  &-icon {
    display: block;
    width: 70px;
    height: 70px;
    padding: var(--el-padding);
    margin: 8px auto 0 auto;
    background: #101f58;
    border-radius: 50%;
    animation: twink 3s linear infinite;
  }

  &-text {
    margin-top: 10px;
    font-size: 30px;
    color: #64c5d9;
    text-align: left;

    p {
      font-size: 14px;
      color: #fff;
    }
  }
}
</style>
