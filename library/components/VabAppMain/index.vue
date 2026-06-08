<template>
  <div class="vab-app-main">
    <section>
      <demo-global-bar v-if="isDemoRoute" :show-all-markets="isDashboardRoute" />
      <vab-router-view />
      <vab-footer />
    </section>
  </div>
</template>

<script lang="ts" setup>
import { useRoutesStore } from '/@/store/modules/routes'
import { handleActivePath } from '/@/utils/routes'
import DemoGlobalBar from '/@/views/demo/components/DemoGlobalBar.vue'

defineOptions({
  name: 'VabAppMain',
})

const route = useRoute()
const routesStore = useRoutesStore()
const { tab, activeMenu } = storeToRefs(routesStore)

const isDemoRoute = computed(() => (route.path as string).startsWith('/demo'))
const isDashboardRoute = computed(() => route.path === '/demo/dashboard' || route.path === '/demo/dashboard/')

watch(
  route,
  () => {
    if (tab.value.data !== route.matched[0].name) tab.value.data = route.matched[0].name as string
    activeMenu.value.data = handleActivePath(route)
  },
  { immediate: true }
)
</script>
