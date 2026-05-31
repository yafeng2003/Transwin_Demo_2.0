/**
 * @description router全局配置，如有必要可分文件抽离，其中asyncRoutes只有在intelligence模式下才会用到，pro版只支持remixIcon图标，具体配置请查看vip群文档
 */
import type { App } from 'vue'
import type { RouteRecordName, RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import { authentication, base, disableRouterWarning, isHashRouterMode } from '/@/config'
import { setupPermissions } from '/@/router/permissions'
import Layout from '/@vab/layouts/index.vue'

export const constantRoutes: VabRouteRecord[] = [
  {
    path: '/',
    redirect: '/demo/dashboard',
    meta: { hidden: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('/@/views/login/Login.vue'),
    meta: { hidden: true },
  },
  {
    path: '/403',
    name: '403',
    component: () => import('/@/views/error/403.vue'),
    meta: { hidden: true },
  },
  {
    path: '/404',
    name: '404',
    component: () => import('/@/views/error/404.vue'),
    meta: { hidden: true },
  },
]

export const asyncRoutes: VabRouteRecord[] = [
  // ==================== 总览 ====================
  {
    path: '/demo/dashboard',
    name: 'Dashboard',
    component: Layout,
    meta: {
      title: '总览',
      icon: 'odometer-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: '',
        name: 'DashboardIndex',
        component: () => import('/@/views/demo/dashboard/index.vue'),
        meta: {
          title: '总览',
          icon: 'odometer-line',
          noColumn: true,
        },
      },
    ],
  },

  // ==================== 策略展示层 ====================
  {
    path: '/demo/strategy',
    name: 'Strategy',
    component: Layout,
    redirect: '/demo/strategy/orders',
    meta: {
      title: '策略展示',
      icon: 'line-chart-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: 'orders',
        name: 'StrategyOrders',
        component: () => import('/@/views/demo/strategy/orders.vue'),
        meta: { title: '订单中心', icon: 'file-list-3-line' },
      },
      {
        path: 'deals',
        name: 'StrategyDeals',
        component: () => import('/@/views/demo/strategy/deals.vue'),
        meta: { title: '成交中心', icon: 'exchange-line' },
      },
      {
        path: 'positions',
        name: 'StrategyPositions',
        component: () => import('/@/views/demo/strategy/positions.vue'),
        meta: { title: '持仓中心', icon: 'archive-line' },
      },
      {
        path: 'account',
        name: 'StrategyAccount',
        component: () => import('/@/views/demo/strategy/account.vue'),
        meta: { title: '账户中心', icon: 'bank-card-line' },
      },
    ],
  },

  // ==================== 风控展示层 ====================
  {
    path: '/demo/risk',
    name: 'Risk',
    component: Layout,
    redirect: '/demo/risk/overview',
    meta: {
      title: '风控展示',
      icon: 'shield-check-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: 'overview',
        name: 'RiskOverview',
        component: () => import('/@/views/demo/risk/overview.vue'),
        meta: { title: '风控总览', icon: 'dashboard-line' },
      },
      {
        path: 'execution',
        name: 'RiskExecution',
        component: () => import('/@/views/demo/risk/execution.vue'),
        meta: { title: '执行风险监控', icon: 'error-warning-line' },
      },
      {
        path: 'account',
        name: 'RiskAccount',
        component: () => import('/@/views/demo/risk/account.vue'),
        meta: { title: '账户风险监控', icon: 'funds-line' },
      },
      {
        path: 'events',
        name: 'RiskEvents',
        component: () => import('/@/views/demo/risk/events.vue'),
        meta: { title: '风险事件中心', icon: 'alert-line' },
      },
      {
        path: 'notifications',
        name: 'RiskNotifications',
        component: () => import('/@/views/demo/risk/notifications.vue'),
        meta: { title: '风险通知中心', icon: 'notification-3-line' },
      },
    ],
  },

  // ==================== 数据分析展示层 ====================
  {
    path: '/demo/analysis',
    name: 'Analysis',
    component: Layout,
    redirect: '/demo/analysis/returns',
    meta: {
      title: '数据分析',
      icon: 'bar-chart-2-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: 'returns',
        name: 'AnalysisReturns',
        component: () => import('/@/views/demo/analysis/returns.vue'),
        meta: { title: '收益分析', icon: 'money-cny-circle-line' },
      },
      {
        path: 'risk',
        name: 'AnalysisRisk',
        component: () => import('/@/views/demo/analysis/risk.vue'),
        meta: { title: '风险分析', icon: 'pulse-line' },
      },
      {
        path: 'trading',
        name: 'AnalysisTrading',
        component: () => import('/@/views/demo/analysis/trading.vue'),
        meta: { title: '交易分析', icon: 'swap-line' },
      },
      {
        path: 'strategy',
        name: 'AnalysisStrategy',
        component: () => import('/@/views/demo/analysis/strategy.vue'),
        meta: { title: '策略分析', icon: 'brain-line' },
      },
      {
        path: 'charts',
        name: 'AnalysisCharts',
        component: () => import('/@/views/demo/analysis/charts.vue'),
        meta: { title: '可视化图表', icon: 'pie-chart-line' },
      },
    ],
  },

  // ==================== 报表中心 ====================
  {
    path: '/demo/reports',
    name: 'Reports',
    component: Layout,
    meta: {
      title: '报表中心',
      icon: 'file-text-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: '',
        name: 'ReportsIndex',
        component: () => import('/@/views/demo/reports/index.vue'),
        meta: {
          title: '报表中心',
          icon: 'file-text-line',
          noColumn: true,
        },
      },
    ],
  },

  // ==================== 日志与通知展示层 ====================
  {
    path: '/demo/logs',
    name: 'Logs',
    component: Layout,
    redirect: '/demo/logs/system',
    meta: {
      title: '日志与通知',
      icon: 'file-list-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: 'system',
        name: 'LogsSystem',
        component: () => import('/@/views/demo/logs/system.vue'),
        meta: { title: '系统日志', icon: 'computer-line' },
      },
      {
        path: 'trading',
        name: 'LogsTrading',
        component: () => import('/@/views/demo/logs/trading.vue'),
        meta: { title: '交易日志', icon: 'exchange-funds-line' },
      },
      {
        path: 'notifications',
        name: 'LogsNotifications',
        component: () => import('/@/views/demo/logs/notifications.vue'),
        meta: { title: '通知中心', icon: 'notification-line' },
      },
    ],
  },

  // ==================== 人工干预层 ====================
  {
    path: '/demo/manual',
    name: 'Manual',
    component: Layout,
    meta: {
      title: '人工干预',
      icon: 'user-voice-line',
      guard: ['Admin'],
    },
    children: [
      {
        path: '',
        name: 'ManualIndex',
        component: () => import('/@/views/demo/manual/index.vue'),
        meta: {
          title: '人工干预',
          icon: 'user-voice-line',
          noColumn: true,
        },
      },
    ],
  },
  // {
  //   path: '/market',
  //   name: 'Market',
  //   component: Layout,
  //   meta: {
  //     title: '市场态势',
  //     icon: 'bar-chart-box-ai-line',
  //     guard: ['Admin'],
  //   },
  //   children: [
  //     {
  //       path: 'situation',
  //       name: 'Situation',
  //       component: () => import('/@/views/market/ashare.vue'),
  //       meta: {
  //         title: 'A股态势',
  //         guard: ['Admin'],
  //         icon: 'bar-chart-box-ai-line',
  //       },
  //     },
  //     {
  //       path: 'pd',
  //       name: 'Pd',
  //       component: () => import('/@/views/market/hkshare.vue'),
  //       meta: {
  //         title: '港股态势',
  //         guard: ['Admin'],
  //         icon: 'bar-chart-box-ai-line',
  //       },
  //     },
      // {
      //   path: 'datas',
      //   name: 'Datas',
      //   component: () => import('/@/views/overall/datas.vue'),
      //   meta: {
      //     title: '总体数据概览',
      //     guard: ['Admin'],
      //     icon: 'bar-chart-box-ai-line',
      //   },
      // },
      // {
      //   path: 'report',
      //   name: 'Report',
      //   component: () => import('/@/views/overall/report.vue'),
      //   meta: {
      //     title: '智能报告生成',
      //     guard: ['Admin'],
      //     icon: 'anthropic-fill',
      //   },
      // },
  //   ],
  // },
  // {
  //   path: '/social',
  //   name: 'Social',
  //   component: Layout,
  //   meta: {
  //     title: '社会管理智能治理',
  //     icon: 'check-double-fill',
  //     guard: ['Admin'],
  //   },
  //   children: [
  //     {
  //       path: 'complaint',
  //       name: 'Complaint',
  //       component: () => import('/@/views/social/complaint.vue'),
  //       meta: {
  //         title: '投诉智能挖掘',
  //         guard: ['Admin'],
  //         icon: 'file-copy-2-line',
  //       },
  //     },
  //     {
  //       path: 'analysis',
  //       name: 'Analysis',
  //       component: () => import('/@/views/social/analysis.vue'),
  //       meta: {
  //         title: '重点问题预警',
  //         guard: ['Admin'],
  //         icon: 'shield-check-fill',
  //       },
  //     },
  //     {
  //       path: 'topics',
  //       name: 'Topics',
  //       component: () => import('/@/views/social/topics.vue'),
  //       meta: {
  //         title: '民生观点感知',
  //         guard: ['Admin'],
  //         icon: 'apps-2-add-line',
  //       },
  //     },
  //     {
  //       path: 'hot',
  //       name: 'Hot',
  //       component: () => import('/@/views/social/hot.vue'),
  //       meta: {
  //         title: '热点事件发现',
  //         guard: ['Admin'],
  //         icon: 'product-hunt-line',
  //       },
  //     },
  //   ],
  // },
  // {
  //   path: '/neweconomy',
  //   name: 'Neweconomy',
  //   component: Layout,
  //   meta: {
  //     title: '经济运行智能研判',
  //     icon: 'ai-generate',
  //     guard: ['Admin'],
  //     // levelHidden: true,
  //     // breadcrumbHidden: true,
  //   },
  //   children: [
  //     {
  //       path: 'consume',
  //       name: 'Consume',
  //       component: () => import('/@/views/newEconomy/consume.vue'),
  //       meta: {
  //         title: '新兴消费感知',
  //         guard: ['Admin'],
  //         icon: 'radar-line',
  //         // noColumn: true,
  //       },
  //     },
  //     {
  //       path: 'trade',
  //       name: 'Trade',
  //       component: () => import('/@/views/newEconomy/trade.vue'),
  //       meta: {
  //         title: '新兴业态研判',
  //         guard: ['Admin'],
  //         icon: 'ai-generate-2',
  //         // noColumn: true,
  //       },
  //     },
  //     {
  //       path: 'compare',
  //       name: 'Compare',
  //       component: () => import('/@/views/newEconomy/compare.vue'),
  //       meta: {
  //         title: '新区对比分析',
  //         guard: ['Admin'],
  //         icon: 'contrast-fill',
  //         // noColumn: true,
  //       },
  //     },
  //     {
  //       path: 'compare1',
  //       name: 'Compare1',
  //       component: () => import('/@/views/newEconomy/compare1.vue'),
  //       meta: {
  //         title: '新区对比分析',
  //         guard: ['Admin'],
  //         icon: 'contrast-fill',
  //         hidden: true,
  //         // noColumn: true,
  //       },
  //     },
  //     {
  //       path: 'ereport',
  //       name: 'EReport',
  //       component: () => import('/@/views/newEconomy/report.vue'),
  //       meta: {
  //         title: '智能决策支持',
  //         guard: ['Admin'],
  //         icon: 'file-chart-line',
  //         // noColumn: true,
  //       },
  //     },
  //   ],
  // },
  // {
  //   path: '/business',
  //   name: 'Business',
  //   component: Layout,
  //   meta: {
  //     title: '城市治理智能优化',
  //     icon: 'brain-fill',
  //     guard: ['Admin'],
  //   },
  //   children: [
  //     {
  //       path: 'assess',
  //       name: 'Assess',
  //       component: () => import('/@/views/business/assess.vue'),
  //       meta: {
  //         title: '智能评价体系',
  //         guard: ['Admin'],
  //         icon: 'anthropic-fill',
  //       },
  //     },
  //     {
  //       path: 'tracing',
  //       name: 'Tracing',
  //       component: () => import('/@/views/business/tracing.vue'),
  //       meta: {
  //         title: '问题感知溯源',
  //         guard: ['Admin'],
  //         icon: 'bar-chart-grouped-fill',
  //       },
  //     },
  //     {
  //       path: 'warning',
  //       name: 'Warning',
  //       component: () => import('/@/views/business/warning.vue'),
  //       meta: {
  //         title: '国际影响分析',
  //         guard: ['Admin'],
  //         icon: 'align-center',
  //       },
  //     },
  //     {
  //       path: 'portray',
  //       name: 'Portray',
  //       component: () => import('/@/views/business/portray.vue'),
  //       meta: {
  //         title: '智能建议生成',
  //         guard: ['Admin'],
  //         icon: 'align-center',
  //       },
  //     },
  //     {
  //       path: 'worldmap',
  //       name: 'Worldmap',
  //       component: () => import('/@/views/business/worldmap.vue'),
  //       meta: {
  //         title: '世界地图',
  //         guard: ['Admin'],
  //         icon: 'align-center',
  //       },
  //     },
  //   ],
  // },
]

const router = createRouter({
  history: isHashRouterMode ? createWebHashHistory(base) : createWebHistory(base),
  routes: constantRoutes as RouteRecordRaw[],
})

const fatteningRoutes = (routes: VabRouteRecord[]): VabRouteRecord[] => {
  return routes.flatMap((route) => {
    return route.children ? fatteningRoutes(route.children) : route
  })
}

const addRouter = (routes: VabRouteRecord[]) => {
  routes.forEach((route: VabRouteRecord) => {
    if (!router.hasRoute(route.name)) router.addRoute(route as RouteRecordRaw)
    if (route.children) addRouter(route.children)
  })
}

export const resetRouter = (routes: VabRouteRecord[] = constantRoutes) => {
  routes.map((route: VabRouteRecord) => {
    if (route.children) route.children = fatteningRoutes(route.children)
  })
  router.getRoutes().forEach((route) => {
    if (route.name) {
      const routeName: RouteRecordName = route.name
      router.hasRoute(routeName) && router.removeRoute(routeName)
    }
  })
  addRouter(routes)
}

export const setupRouter = (app: App<Element>) => {
  /*
   * @description: 控制台禁止出现[Vue Router warn]: No match found for location with path "/index"报黄
   * @tips: 未经全面测试，请谨慎使用！如遇问题请前往config/cli.config.ts配置disableRouterWarning:false
   * @author: @sundan
   */
  if (disableRouterWarning)
    router.addRoute({
      path: '/:pathMatch(.*)*',
      component: () => {},
    })

  if (authentication === 'intelligence') addRouter(asyncRoutes)
  setupPermissions(router)
  app.use(router)

  return router
}

export default router
