<template>
  <div
    class="vab-layout-vertical"
    :class="{
      fixed: fixedHeader,
      'no-tabs-bar': !showTabs,
    }"
  >
    <vab-side-bar />
    <div v-if="device === 'mobile' && !collapse" class="vab-modal" @click="foldSideBar"></div>
    <div
      class="vab-main"
      :class="{
        'is-collapse-main': collapse,
        'is-no-tabs': !showTabs,
      }"
    >
      <div
        class="vab-layout-header"
        :class="{
          'fixed-header': fixedHeader,
          'is-no-tabs': !showTabs,
        }"
      >
        <!-- <vab-nav /> -->
        <data-screen-header />
        <vab-tabs v-show="showTabs" />
      </div>
      <vab-app-main />
    </div>
  </div>
</template>

<script lang="ts" setup>
import dataScreenHeader from './DataScreenHeader.vue'
import { useSettingsStore } from '/@/store/modules/settings'

defineOptions({
  name: 'VabLayoutVertical',
})

defineProps({
  collapse: {
    type: Boolean,
    default: false,
  },
  fixedHeader: {
    type: Boolean,
    default: true,
  },
  showTabs: {
    type: Boolean,
    default: true,
  },
  device: {
    type: String,
    default: 'desktop',
  },
})

const settingsStore = useSettingsStore()
const { foldSideBar } = settingsStore
</script>

<style lang="css" scoped>
vab-app-main {
  margin-top: 30px;
}
</style>
