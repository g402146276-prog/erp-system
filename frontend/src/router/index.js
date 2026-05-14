import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { noAuth: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/inbound-list',
    name: 'InboundList',
    component: () => import('../views/InboundList.vue'),
    meta: { title: '入库记录' }
  },
  {
    path: '/transfer-list',
    name: 'TransferList',
    component: () => import('../views/TransferList.vue'),
    meta: { title: '调拨记录' }
  },
  {
    path: '/stock',
    name: 'Stock',
    component: () => import('../views/Stock.vue'),
    meta: { title: '库存查询' }
  },
  {
    path: '/goods-import',
    name: 'GoodsImport',
    component: () => import('../views/GoodsImport.vue'),
    meta: { title: '商品档案' }
  },
  {
    path: '/persons',
    name: 'Persons',
    component: () => import('../views/Persons.vue'),
    meta: { title: '人员档案' }
  },
  {
    path: '/suppliers',
    name: 'Suppliers',
    component: () => import('../views/Suppliers.vue'),
    meta: { title: '供应商档案' }
  },
  // ===== 新增模块 =====
  {
    path: '/scan',
    name: 'Scan',
    component: () => import('../views/Scan.vue'),
    meta: { title: '扫码查货' }
  },
  {
    path: '/goods-detail/:id',
    name: 'GoodsDetail',
    component: () => import('../views/GoodsDetail.vue'),
    meta: { title: '商品详情' }
  },
  {
    path: '/quick-adjust',
    name: 'QuickAdjust',
    component: () => import('../views/QuickAdjust.vue'),
    meta: { title: '快速盘点' }
  },
  {
    path: '/adjustment-list',
    name: 'AdjustmentList',
    component: () => import('../views/AdjustmentList.vue'),
    meta: { title: '调整单' }
  },
  {
    path: '/locations',
    name: 'Locations',
    component: () => import('../views/Locations.vue'),
    meta: { title: '货位管理' }
  },
  // ===== 新模块 =====
  {
    path: '/purchase-inbound',
    name: 'PurchaseInbound',
    component: () => import('../views/PurchaseInbound.vue'),
    meta: { title: '采购入库' }
  },
  {
    path: '/intransit-orders',
    name: 'IntransitOrder',
    component: () => import('../views/IntransitOrder.vue'),
    meta: { title: '在途订单' }
  },
  {
    path: '/transfer-apply',
    name: 'TransferApply',
    component: () => import('../views/TransferApply.vue'),
    meta: { title: '调拨申请单' }
  },
  {
    path: '/outbound',
    name: 'OutboundOrder',
    component: () => import('../views/OutboundOrder.vue'),
    meta: { title: '出库单' }
  },
  {
    path: '/gift-orders',
    name: 'GiftOrder',
    component: () => import('../views/GiftOrder.vue'),
    meta: { title: '赠送单' }
  },
  {
    path: '/approval-rules',
    name: 'ApprovalRules',
    component: () => import('../views/ApprovalRules.vue'),
    meta: { title: '审批规则' }
  },
  {
    path: '/reconciliation',
    name: 'Reconciliation',
    component: () => import('../views/Reconciliation.vue'),
    meta: { title: '对账看板' }
  },
  {
    path: '/warehouses',
    name: 'Warehouses',
    component: () => import('../views/Warehouses.vue'),
    meta: { title: '仓库管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('erp_token')
  if (to.path === '/login') {
    if (token) {
      next('/')
    } else {
      next()
    }
    return
  }
  if (!token) {
    next('/login')
    return
  }
  next()
})

export default router
