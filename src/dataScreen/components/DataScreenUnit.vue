<template>
  <!-- <el-row class="data-screen-uperbottom" :gutter="0">
    <el-col :span="2" />
    <el-col :span="2.3">
      <div>委托单位：</div>
    </el-col>
    <el-col :span="17">外交学院</el-col>
    <el-col :span="17" />
  </el-row> -->
  <el-row class="data-screen-bottom" :gutter="0">
    <el-col :span="2" />
    <el-col :span="2.3">
      <div>Powered by：</div>
    </el-col>
    <el-col :span="17">Global Mind</el-col>
    <!-- <el-col :span="8">北京大学（青岛）计算社会科学研究院</el-col> -->
    <el-col :span="17" />
  </el-row>
</template>

<script lang="ts" setup>
defineOptions({
  name: 'DataScreenBottom',
})
</script>

<style lang="scss" scoped>
.data-screen-uperbottom {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 1rem;
  padding-left: 35%;
  // font-weight: 600;
}
.data-screen-bottom {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 1rem;
  padding-left: 23%;
  // font-weight: 600;
}
</style>

ss
