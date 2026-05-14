<template>
  <div id="app">
    <!-- 登录页不显示主布局 -->
    <template v-if="isLoginPage">
      <router-view />
    </template>
    <template v-else>
      <el-container class="erp-layout">
        <!-- 左侧导航菜单 -->
        <el-aside :width="isCollapse ? '64px' : '220px'" class="erp-sidebar">
          <div class="logo-area">
            <div class="logo-icon">📦</div>
            <span v-show="!isCollapse" class="logo-text">仓库ERP</span>
          </div>

          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapse"
            :router="true"
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
            class="erp-menu"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <template #title>首页</template>
            </el-menu-item>

            <el-menu-item index="/scan">
              <el-icon><Camera /></el-icon>
              <template #title>扫码查货</template>
            </el-menu-item>

            <el-sub-menu index="/inbound-module">
              <template #title>
                <el-icon><Box /></el-icon>
                <span>入库管理</span>
              </template>
              <el-menu-item index="/purchase-inbound">采购入库</el-menu-item>
              <el-menu-item index="/intransit-orders">在途订单</el-menu-item>
              <el-menu-item index="/inbound-list">入库记录</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/outbound-module">
              <template #title>
                <el-icon><TakeawayBox /></el-icon>
                <span>出库管理</span>
              </template>
              <el-menu-item index="/outbound">出库单</el-menu-item>
              <el-menu-item index="/gift-orders">赠送单</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="/transfer-module">
              <template #title>
                <el-icon><RefreshRight /></el-icon>
                <span>调拨管理</span>
              </template>
              <el-menu-item index="/transfer-apply">调拨申请单</el-menu-item>
              <el-menu-item index="/transfer-list">调拨记录</el-menu-item>
            </el-sub-menu>

            <el-menu-item index="/stock">
              <el-icon><Coin /></el-icon>
              <template #title>库存查询</template>
            </el-menu-item>

            <el-menu-item index="/reconciliation">
              <el-icon><DataAnalysis /></el-icon>
              <template #title>对账看板</template>
            </el-menu-item>

            <el-menu-item index="/adjustment-list">
              <el-icon><EditPen /></el-icon>
              <template #title>盘点调整</template>
            </el-menu-item>

            <el-menu-item index="/locations">
              <el-icon><Grid /></el-icon>
              <template #title>货位管理</template>
            </el-menu-item>

            <el-sub-menu index="/system-module">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>系统管理</span>
              </template>
              <el-menu-item index="/warehouses">仓库管理</el-menu-item>
              <el-menu-item index="/approval-rules">审批规则</el-menu-item>
              <el-menu-item index="/goods-import">商品档案</el-menu-item>
              <el-menu-item index="/persons">人员档案</el-menu-item>
              <el-menu-item index="/suppliers">供应商档案</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>

        <el-container>
          <!-- 顶部工具栏 -->
          <el-header class="erp-header">
            <div class="header-left">
              <el-button text @click="isCollapse = !isCollapse" class="collapse-btn">
                <el-icon v-if="isCollapse"><Expand /></el-icon>
                <el-icon v-else><Fold /></el-icon>
              </el-button>

              <el-breadcrumb separator="/" class="breadcrumb">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item v-if="currentModule">{{ currentModule }}</el-breadcrumb-item>
                <el-breadcrumb-item v-if="currentPage">{{ currentPage }}</el-breadcrumb-item>
              </el-breadcrumb>
            </div>

            <div class="header-right">
              <el-dropdown @command="handleCommand" trigger="click">
                <div class="user-info">
                  <el-avatar size="small">{{ user.display_name?.charAt(0) || '管' }}</el-avatar>
                  <span class="username">{{ user.display_name || '用户' }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon> 个人中心
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon> 退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-header>

          <!-- 主内容区 -->
          <el-main class="erp-main">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </el-main>
        </el-container>
      </el-container>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  HomeFilled, Camera, Box, TakeawayBox, RefreshRight, Coin,
  EditPen, Grid, DataAnalysis, Setting, Expand, Fold,
  ArrowDown, User, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)

const user = ref(JSON.parse(localStorage.getItem('erp_user') || '{}'))

const isLoginPage = computed(() => route.path === '/login')

const menuMap = {
  '/': { module: '', page: '首页' },
  '/scan': { module: '快捷操作', page: '扫码查货' },
  '/purchase-inbound': { module: '入库管理', page: '采购入库' },
  '/intransit-orders': { module: '入库管理', page: '在途订单' },
  '/inbound-list': { module: '入库管理', page: '入库记录' },
  '/outbound': { module: '出库管理', page: '出库单' },
  '/gift-orders': { module: '出库管理', page: '赠送单' },
  '/transfer-apply': { module: '调拨管理', page: '调拨申请单' },
  '/transfer-list': { module: '调拨管理', page: '调拨记录' },
  '/stock': { module: '库存查询', page: '库存查询' },
  '/reconciliation': { module: '库存查询', page: '对账看板' },
  '/adjustment-list': { module: '库存管理', page: '盘点调整' },
  '/locations': { module: '仓库管理', page: '货位管理' },
  '/warehouses': { module: '系统管理', page: '仓库管理' },
  '/approval-rules': { module: '系统管理', page: '审批规则' },
  '/goods-import': { module: '系统管理', page: '商品档案' },
  '/persons': { module: '系统管理', page: '人员档案' },
  '/suppliers': { module: '系统管理', page: '供应商档案' },
  '/goods-detail/:id': { module: '库存查询', page: '商品详情' },
  '/quick-adjust': { module: '库存管理', page: '快速盘点' }
}

const currentModule = computed(() => {
  const path = route.path
  if (menuMap[path]) return menuMap[path].module
  if (path.startsWith('/goods-detail/')) return '库存查询'
  if (path.startsWith('/quick-adjust')) return '盘点管理'
  return ''
})

const currentPage = computed(() => {
  const path = route.path
  if (menuMap[path]) return menuMap[path].page
  if (path.startsWith('/goods-detail/')) return '商品详情'
  if (path.startsWith('/quick-adjust')) return '快速盘点'
  return ''
})

const activeMenu = computed(() => {
  const path = route.path
  if (menuMap[path]) return path
  if (path.startsWith('/purchase-inbound') || path.startsWith('/intransit') || path.startsWith('/inbound')) return '/inbound-module'
  if (path.startsWith('/outbound') || path.startsWith('/gift')) return '/outbound-module'
  if (path.startsWith('/transfer')) return '/transfer-module'
  if (path.startsWith('/goods-detail/')) return '/stock'
  if (path.startsWith('/quick-adjust')) return '/adjustment-list'
  if (path.startsWith('/approval') || path.startsWith('/goods') || path.startsWith('/person') || path.startsWith('/supplier')) return '/system-module'
  return '/'
})

const handleCommand = (command) => {
  switch (command) {
    case 'logout':
      localStorage.removeItem('erp_token')
      localStorage.removeItem('erp_user')
      router.push('/login')
      ElMessage.success('已退出登录')
      break
    case 'profile':
      ElMessage.info(`当前用户: ${user.value.display_name} (${user.value.role})`)
      break
  }
}

onMounted(() => {
  // 路由变化后刷新用户信息
  router.afterEach(() => {
    try {
      user.value = JSON.parse(localStorage.getItem('erp_user') || '{}')
    } catch (_) {}
  })
})
</script>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }
#app { height: 100vh; overflow: hidden; }
.erp-layout { height: 100vh; }
.erp-sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.logo-icon { font-size: 24px; margin-right: 8px; }
.logo-text { font-size: 18px; font-weight: bold; color: #fff; white-space: nowrap; }
.erp-menu { border-right: none; }
.erp-menu:not(.el-menu--collapse) { width: 220px; }
.erp-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 100;
}
.header-left { display: flex; align-items: center; gap: 20px; }
.collapse-btn { padding: 8px; border-radius: 4px; }
.collapse-btn:hover { background: #f5f7fa; }
.breadcrumb { font-size: 14px; }
.header-right { display: flex; align-items: center; gap: 20px; }
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}
.user-info:hover { background: #f5f7fa; }
.username { font-size: 14px; color: #303133; }
.erp-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
:deep(.el-menu--vertical) { border-right: none; }
</style>
