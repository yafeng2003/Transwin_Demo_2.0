
<template>
  <vab-chart :option="option" />
</template>

<script lang="ts" setup>
import { onBeforeUnmount, onMounted } from 'vue'

defineOptions({
  name: 'DataScreenRight1',
})

const monthCategories = [
  '24年11月',
  '24年12月',
  '25年1月',
  '25年2月',
  '25年3月',
  '25年4月',
  '25年5月',
  '25年6月',
  '25年7月',
  '25年8月',
]
// Data sets for different scenarios
const dataSets = [
  // Original data set
  {
    name: 'Set 1',
    dataTechSupervision: [
      [0, 42, 15],
      [1, 50, 20],
      [2, 40, 25],
      [3, 60, 22],
      [4, 55, 18],
      [5, 65, 24],
      [6, 58, 20],
      [7, 68, 23],
      [8, 52, 17],
      [9, 35, 20],
    ],
    dataDeptResponsibility: [
      [0, 30, 10],
      [1, 45, 16],
      [2, 38, 25],
      [3, 48, 17],
      [4, 35, 21],
      [5, 42, 15],
      [6, 32, 10],
      [7, 40, 14],
      [8, 30, 20],
      [9, 40, 14],
    ],
    dataBusinessAssessment: [
      [0, 55, 20],
      [1, 45, 16],
      [2, 60, 22],
      [3, 52, 18],
      [4, 63, 23],
      [5, 50, 17],
      [6, 62, 22],
      [7, 53, 18],
      [8, 65, 24],
      [9, 50, 18],
    ],
    dataEmployeeCommunication: [
      [0, 40, 13],
      [1, 52, 18],
      [2, 45, 15],
      [3, 55, 19],
      [4, 42, 14],
      [5, 58, 20],
      [6, 48, 16],
      [7, 56, 19],
      [8, 45, 19],
      [9, 48, 16],
    ],
    dataOverseasInspection: [
      [0, 38, 13],
      [1, 28, 9],
      [2, 36, 20],
      [3, 32, 10],
      [4, 40, 14],
      [5, 34, 11],
      [6, 39, 13],
      [7, 31, 10],
      [8, 37, 12],
      [9, 30, 15],
    ],
  },
  // Second data set - more balanced distribution
  {
    name: 'Set 2',
    dataTechSupervision: [
      [0, 45, 16],
      [1, 52, 19],
      [2, 42, 22],
      [3, 58, 20],
      [4, 50, 17],
      [5, 62, 22],
      [6, 55, 19],
      [7, 65, 21],
      [8, 48, 16],
      [9, 38, 18],
    ],
    dataDeptResponsibility: [
      [0, 28, 9],
      [1, 40, 14],
      [2, 33, 20],
      [3, 45, 15],
      [4, 32, 18],
      [5, 38, 13],
      [6, 30, 9],
      [7, 37, 12],
      [8, 28, 17],
      [9, 35, 12],
    ],
    dataBusinessAssessment: [
      [0, 52, 18],
      [1, 42, 14],
      [2, 55, 20],
      [3, 50, 16],
      [4, 60, 21],
      [5, 48, 15],
      [6, 58, 20],
      [7, 50, 16],
      [8, 62, 22],
      [9, 48, 16],
    ],
    dataEmployeeCommunication: [
      [0, 38, 12],
      [1, 50, 17],
      [2, 42, 14],
      [3, 52, 18],
      [4, 40, 13],
      [5, 55, 19],
      [6, 45, 15],
      [7, 53, 18],
      [8, 42, 17],
      [9, 45, 15],
    ],
    dataOverseasInspection: [
      [0, 35, 12],
      [1, 25, 8],
      [2, 33, 18],
      [3, 30, 9],
      [4, 38, 13],
      [5, 32, 10],
      [6, 36, 12],
      [7, 29, 9],
      [8, 34, 11],
      [9, 28, 14],
    ],
  },
  // Third data set - more extreme values
  {
    name: 'Set 3',
    dataTechSupervision: [
      [0, 40, 18],
      [1, 55, 24],
      [2, 35, 28],
      [3, 65, 25],
      [4, 50, 20],
      [5, 70, 28],
      [6, 60, 22],
      [7, 72, 26],
      [8, 45, 19],
      [9, 30, 22],
    ],
    dataDeptResponsibility: [
      [0, 35, 12],
      [1, 50, 18],
      [2, 40, 28],
      [3, 55, 20],
      [4, 38, 24],
      [5, 45, 17],
      [6, 35, 12],
      [7, 45, 16],
      [8, 35, 24],
      [9, 45, 16],
    ],
    dataBusinessAssessment: [
      [0, 60, 22],
      [1, 50, 18],
      [2, 65, 25],
      [3, 58, 20],
      [4, 68, 26],
      [5, 55, 19],
      [6, 67, 24],
      [7, 58, 20],
      [8, 70, 28],
      [9, 55, 20],
    ],
    dataEmployeeCommunication: [
      [0, 45, 15],
      [1, 58, 20],
      [2, 50, 17],
      [3, 60, 21],
      [4, 45, 16],
      [5, 62, 22],
      [6, 52, 18],
      [7, 60, 21],
      [8, 50, 22],
      [9, 52, 18],
    ],
    dataOverseasInspection: [
      [0, 42, 15],
      [1, 32, 11],
      [2, 40, 22],
      [3, 35, 12],
      [4, 45, 16],
      [5, 38, 13],
      [6, 42, 15],
      [7, 35, 12],
      [8, 40, 14],
      [9, 35, 18],
    ],
  },
]

const itemStyle = {
  opacity: 0.8,
  shadowBlur: 10,
  shadowOffsetX: 0,
  shadowOffsetY: 0,
  shadowColor: 'rgba(0,0,0,0.3)',
}

const option = reactive<any>({
  color: ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6'],
  legend: {
    // top: 10,
    left: '20%',
    data: ['政策动向', '能源革新', '智造未来', '银发经济', '数据浪潮'],
    textStyle: {
      fontSize: 12,
      // fontWeight: 'bold',
      color: '#ffffff',
    },
  },
  grid: {
    left: '10%',
    right: '12%',
    top: '30%',
    bottom: '15%',
  },
  tooltip: {
    backgroundColor: 'rgba(255,255,255,0.9)',
    borderWidth: 1,
    borderColor: '#ccc',
    formatter(param: any) {
      return `<div style="border-bottom: 1px solid #eee; font-size: 16px;padding-bottom: 7px;margin-bottom: 7px">${
        param.seriesName
      } - ${monthCategories[param.value[0]]}：主题热度 ${param.value[1]}</div>`
    },
  },
  xAxis: {
    type: 'category',
    name: '月份',
    nameGap: 20,
    nameTextStyle: {
      fontSize: 12,
      // fontWeight: 'bold',
      color: '#ffffff',
    },
    data: monthCategories,
    axisLabel: {
      fontSize: 12,
      color: '#ffffff',
      interval: 2,
      // rotate: 25,
    },
    axisLine: {
      show: true,
      lineStyle: {
        color: '#ffffff',
      },
    },
    axisTick: {
      show: true,
      alignWithLabel: true,
    },
    splitLine: {
      show: false,
    },
  },
  yAxis: {
    type: 'value',
    name: '问题数量',
    nameLocation: 'end',
    // nameGap: 30,
    nameTextStyle: {
      fontSize: 12,
      // fontWeight: 'bold',
      color: '#ffffff',
    },
    axisLabel: {
      fontSize: 12,
      // fontWeight: 'bold',
      color: '#ffffff',
    },
    axisLine: {
      show: true,
      lineStyle: {
        color: '#ffffff',
      },
    },
    splitLine: {
      show: false,
    },
  },
  series: [
    {
      name: '政策动向',
      type: 'scatter',
      symbolSize(data: any) {
        return (data[2] * 2) / 3
      },
      itemStyle,
      data: [],
    },
    {
      name: '能源革新',
      type: 'scatter',
      symbolSize(data) {
        return (data[2] * 2) / 3
      },
      itemStyle,
      data: [],
    },
    {
      name: '智造未来',
      type: 'scatter',
      symbolSize(data) {
        return (data[2] * 2) / 3
      },
      itemStyle,
      data: [],
    },
    {
      name: '银发经济',
      type: 'scatter',
      symbolSize(data) {
        return (data[2] * 2) / 3
      },
      itemStyle,
      data: [],
    },
    {
      name: '数据浪潮',
      type: 'scatter',
      symbolSize(data) {
        return (data[2] * 2) / 3
      },
      itemStyle,
      data: [],
    },
  ],
})

let currentDataSetIndex = 0
let timer: number | null = null

const updateChartData = () => {
  const currentDataSet = dataSets[currentDataSetIndex]

  option.series[0].data = currentDataSet.dataTechSupervision
  option.series[1].data = currentDataSet.dataDeptResponsibility
  option.series[2].data = currentDataSet.dataBusinessAssessment
  option.series[3].data = currentDataSet.dataEmployeeCommunication
  option.series[4].data = currentDataSet.dataOverseasInspection

  // Update the option reference to trigger re-render
  option.value = { ...option.value }

  // Rotate to next data set
  currentDataSetIndex = (currentDataSetIndex + 1) % dataSets.length
}

// Initialize with first data set
updateChartData()

onMounted(() => {
  // Set up timer to switch data every 5 seconds
  timer = globalThis.setInterval(updateChartData, 2000)
})

onBeforeUnmount(() => {
  // Clean up timer when component is destroyed
  if (timer) {
    clearInterval(timer)
  }
})
</script>
