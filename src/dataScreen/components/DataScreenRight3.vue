<template>
  <vab-chart :option="option" />
</template>

<script lang="ts" setup>
import { reactive } from 'vue'

defineOptions({
  name: 'TextScrollDisplay',
})

// 10条文字内容
const textData = [
  '· 布局人工智能与科技板块：企业盈利改善，“十五五”...',
  '· 关注高股息策略：在利率下行和市场波动环境中，高股...',
  '· 增配港股保险股：行业存在较大预期差，且“十五五...',
  '· 参与固定收益市场发展：香港正推出发展路线图，着...',
  '· 把握离岸人民币业务机遇：香港是全球最大离岸人民...',
  '· 跟踪有色金属板块：美联储降息预期可能导致美元走弱...',
  '· 关注金融创新与资产代币化：香港政府正积极推动资产...',
  '· 挖掘新股融资市场机会：香港新股融资市场活力强劲，上...',
]

let currentIndex = 0
const showCount = 5 // 每次显示5条
const itemHeight = 36 // 每条高度
const itemWidth = 400 // 每条宽度
const borderRadius = 4 // 圆角半径

// 创建graphic元素（带背景框）
const createTextElements = () => {
  const elements = []
  const colors = [
    'rgba(0, 179, 244, 0.7)',
    'rgba(0, 199, 224, 0.7)',
    'rgba(0, 219, 204, 0.7)',
    'rgba(0, 239, 184, 0.7)',
    'rgba(0, 159, 264, 0.7)',
  ]

  for (let i = 0; i < showCount; i++) {
    // 先添加背景框
    elements.push(
      {
        type: 'rect',
        left: 0,
        top: 20 + i * itemHeight,
        shape: {
          width: itemWidth,
          height: itemHeight - 8,
          r: borderRadius,
        },
        style: {
          fill: colors[i % colors.length],
        },
        z: 0,
      },
      {
        type: 'text',
        left: 6,
        top: 30 + i * itemHeight,
        style: {
          text: textData[(currentIndex + i) % textData.length],
          font: '14px Microsoft YaHei',
          fill: '#fff',
          textAlign: 'center',
          // fontWeight: 'bold',
          fontSize: 15, // 单独设置字号
        },
        z: 1,
      }
    )
  }
  return elements
}

const option = reactive<any>({
  grid: {
    top: '0',
    left: '0',
    right: '0',
    bottom: '0',
    containLabel: true,
  },
  // 禁用不必要的组件
  xAxis: { show: false },
  yAxis: { show: false },
  series: [],
  graphic: createTextElements(),
})

// 更新图表
const updateChart = () => {
  currentIndex = (currentIndex + 1) % textData.length
  option.graphic = createTextElements()
}

// 设置定时器，每2秒滚动一次
setInterval(updateChart, 2000)
</script>
