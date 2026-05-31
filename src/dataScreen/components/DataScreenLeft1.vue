<template>
  <vab-chart :option="option" />
</template>

<script lang="ts" setup>
import { graphic } from 'echarts/core'
import { random } from 'lodash-es'

defineOptions({
  name: 'DataScreenLeft2',
})

const option = reactive<any>({
  grid: {
    left: '0',
    right: '0',
    bottom: '0',
    top: '10px',
    containLabel: true,
  },
  tooltip: {
    trigger: 'axis',
  },
  xAxis: {
    show: false,
    type: 'value',
    axisLabel: {
      color: '#eee',
    },
    boundaryGap: false,
    splitLine: {
      show: false,
    },
  },
  yAxis: [
    {
      type: 'category',
      inverse: true,
      data: [
        '汇川朱兴明：瞄准工业无线化未来',
        '「零重力飞机工业」完成融资',
        '华泰创星CEO全球加速营',
        '高端泳池机器人品牌完成融资',
      ],
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      splitLine: {
        show: false,
      },
      axisLabel: {
        color: '#fff',
        fontSize: '14px',
      },
    },
  ],
  series: {
    name: '',
    type: 'bar',
    zlevel: 1,
    itemStyle: {
      borderRadius: 10,
      color: new graphic.LinearGradient(0, 0, 1, 0, [
        {
          offset: 0,
          color: 'rgb(57,89,255,1)',
        },
        {
          offset: 1,
          color: 'rgb(46,200,207,1)',
        },
      ]),
    },
    barWidth: 15,
    data: [random(75, 100), random(75, 100), random(75, 100), random(75, 100)],
    label: {
      show: true,
      position: 'inside',
      color: '#fff',
    },
  },
})

const unitName = [
  '特斯联与优必选达成战略合作',
  'AI重塑海外营销',
  '巴西法律人工智能企业完成融资',
  '加密货币初创公司完成融资',
  '“第二人生”完成数千万股权融资',
  '“诺亦腾机器人”完成天使轮融资',
  '见荨“草本汉堡”获融资',
  '云枢智航完成近亿元天使轮融资',
  '安德科铭半导体完成E轮融资',
  '“零重力飞机工业”完成A++轮融资',
]

setInterval(() => {
  const indices = Array.from({ length: unitName.length }, (_, i) => i)
  indices.sort(() => Math.random() - 0.5)
  option.yAxis[0].data = indices.slice(0, 4).map((index) => unitName[index])
  option.series.data = [random(75, 100), random(75, 100), random(75, 100), random(75, 100)]
}, 1000 * 5)
</script>