<template>
  <el-row>
    <el-col :span="24">
      <div class="header-background">
        <div class="data-screen-header hidden-xs-only">
          <!-- <vab-link target="_blank" to="/home">
          <div class="data-go-home">
            <vab-icon icon="home-2-line" />
          </div>
        </vab-link> -->
          <span :data-title="title">{{ title }}</span>
          <!-- <vab-fullscreen class="data-fullscreen" /> -->
        </div>
      </div>

      <!-- <div class="data-screen-header hidden-sm-and-up mobile-only">
        <vab-link target="_blank" to="/index">
          <div class="data-go-home">
            <vab-icon icon="home-2-line" />
          </div>
        </vab-link>
        <div class="mobile-title">数据大屏</div>
        <vab-fullscreen class="data-fullscreen" />
      </div> -->
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 如果是大屏（DataScreen 或 Dindex），保留旧的品牌写法；其它页面显示带 s 的 Transwin
const title = computed(() => {
  const name = String(route.name)
  // 统一为 TransWin（T 和 W 大写）用于显示
  return 'TransWin智赢证券投资系统'
})
</script>

<style lang="scss" scoped>
@keyframes flare {
  0% {
    background-position: -400px;
  }

  30% {
    background-position: 0;
  }

  100% {
    background-position: 400px;
    opacity: 0;
  }
}
.header-background {
  width: 100%;
  height: 64px;
  margin-bottom: 20px;
  background: #010c21;
}
.data-screen-header {
  width: 100%;
  // height: var(--el-nav-height);
  height: 64px;
  margin-bottom: 20px;
  text-align: center;
  background: url('/@/assets/data_screen_images/bgtop.png') no-repeat center;
  background-size: 135% 100%;

  span {
    position: relative;
    top: 23%;
    font-size: 1.7rem;
    font-weight: bold;
    color: #33e6fa;
    background: linear-gradient(
      -90deg,
      #7cedfb 0%,
      #2ba3ff 0%,
      #02efff 50.2685546875%,
      #2ea5f9 100%
    );
    background-clip: text;
    -webkit-text-fill-color: transparent;

    &::before {
      position: absolute;
      left: 0;
      display: block;
      width: 100%;
      color: #fff;
      /* use attr(data-title) so pseudo elements match the dynamic title */
      content: attr(data-title);
      background-image: linear-gradient(
        65deg,
        transparent 10%,
        rgba(255, 255, 255, 1) 20%,
        rgba(255, 255, 255, 1) 27.5%,
        transparent 30%,
        transparent 100%
      );
      background-clip: text;
      animation: flare 3s infinite;
    }

    &::after {
      position: absolute;
      top: 0;
      z-index: -1;
      display: block;
      color: #fff;
      content: attr(data-title);
    }
  }

  &.mobile-only {
    .data-fullscreen,
    .data-go-home {
      width: 40px;
      height: 40px;
    }

    .mobile-title {
      position: relative;
      font-size: var(--el-font-size-extra-large);
      font-weight: bold;
      color: #33e6fa;
      background: linear-gradient(
        -90deg,
        #7cedfb 0%,
        #2ba3ff 0%,
        #02efff 50.2685546875%,
        #2ea5f9 100%
      );
      background-clip: text;
      -webkit-text-fill-color: transparent;

      &::before {
        position: absolute;
        left: 0;
        display: block;
        width: 100%;
        color: #fff;
        content: '数据大屏';
        background-image: linear-gradient(
          65deg,
          transparent 10%,
          rgba(255, 255, 255, 1) 20%,
          rgba(255, 255, 255, 1) 27.5%,
          transparent 30%,
          transparent 100%
        );
        background-clip: text;
        animation: flare 3s infinite;
      }

      &::after {
        position: absolute;
        top: 0;
        z-index: -1;
        display: block;
        color: #fff;
        content: '数据大屏';
      }
    }
  }
}
</style>
