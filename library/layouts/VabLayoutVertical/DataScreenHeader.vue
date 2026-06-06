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
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
}
.data-screen-header {
  width: 100%;
  height: 64px;
  margin-bottom: 20px;
  text-align: center;
  background: linear-gradient(180deg, #e8f4fd 0%, #ffffff 100%);

  span {
    position: relative;
    top: 23%;
    font-size: 1.7rem;
    font-weight: bold;
    color: #1a5fa8;
    background: linear-gradient(
      -90deg,
      #1a5fa8 0%,
      #4e88f3 0%,
      #1a7ec8 50.2685546875%,
      #4e88f3 100%
    );
    background-clip: text;
    -webkit-text-fill-color: transparent;

    &::before {
      position: absolute;
      left: 0;
      display: block;
      width: 100%;
      color: #1a5fa8;
      content: attr(data-title);
      background-image: linear-gradient(
        65deg,
        transparent 10%,
        rgba(78, 136, 243, 0.4) 20%,
        rgba(78, 136, 243, 0.6) 27.5%,
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
      color: #1a5fa8;
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
      color: #1a5fa8;
      background: linear-gradient(
        -90deg,
        #1a5fa8 0%,
        #4e88f3 0%,
        #1a7ec8 50.2685546875%,
        #4e88f3 100%
      );
      background-clip: text;
      -webkit-text-fill-color: transparent;

      &::before {
        position: absolute;
        left: 0;
        display: block;
        width: 100%;
        color: #1a5fa8;
        content: '数据大屏';
        background-image: linear-gradient(
          65deg,
          transparent 10%,
          rgba(78, 136, 243, 0.4) 20%,
          rgba(78, 136, 243, 0.6) 27.5%,
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
        color: #1a5fa8;
        content: '数据大屏';
      }
    }
  }
}
</style>
