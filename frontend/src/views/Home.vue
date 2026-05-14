<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>今日入库</span>
            </div>
          </template>
          <div class="stat-number">{{ todayInbound }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>今日调拨</span>
            </div>
          </template>
          <div class="stat-number">{{ todayTransfer }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>待入库申请</span>
            </div>
          </template>
          <div class="stat-number">{{ pendingApply }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>库存预警</span>
            </div>
          </template>
          <div class="stat-number">{{ stockWarning }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="danger" @click="$router.push('/scan')">📷 扫码查货</el-button>
            <el-button type="primary" @click="$router.push('/purchase-inbound')">采购入库</el-button>
            <el-button type="success" @click="$router.push('/transfer-apply')">调拨申请单</el-button>
            <el-button type="warning" @click="$router.push('/inbound-apply')">入库申请</el-button>
            <el-button type="info" @click="$router.push('/stock')">库存查询</el-button>
            <el-button @click="$router.push('/adjustment-list')">📌 调整单</el-button>
            <el-button @click="$router.push('/locations')">货位管理</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待处理事项</span>
            </div>
          </template>
          <el-empty v-if="pendingTasks.length === 0" description="暂无待处理事项" />
          <el-list v-else>
            <el-list-item v-for="task in pendingTasks" :key="task.id">
              <el-tag :type="task.type">{{ task.tag }}</el-tag>
              <span style="margin-left: 10px;">{{ task.content }}</span>
            </el-list-item>
          </el-list>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { inboundApi, inboundApplyApi, transferApi } from '../api/modules'
import { adjustmentApi } from '../api/modules_ext'

const todayInbound = ref(0)
const todayTransfer = ref(0)
const pendingApply = ref(0)
const stockWarning = ref(0)
const pendingTasks = ref([])

onMounted(async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    const inboundList = await inboundApi.list()
    todayInbound.value = inboundList.filter(item => item.created_at && item.created_at.startsWith(today)).length

    const transferList = await transferApi.list({ status: 'pending' })
    todayTransfer.value = transferList.length

    const applyList = await inboundApplyApi.list({ status: 'pending' })
    pendingApply.value = applyList.length

    const pendingAdjustments = await adjustmentApi.list({ status: 'pending' })
    stockWarning.value = pendingAdjustments.filter(a => a.diff_qty < 0).length

    pendingTasks.value = [
      { id: 1, type: 'warning', tag: '入库申请', content: `${pendingApply.value}个入库申请待处理` },
      { id: 2, type: 'info', tag: '调拨', content: `${todayTransfer.value}个调拨待审批` },
      ...pendingAdjustments.slice(0, 3).map((a, i) => ({
        id: 100 + i,
        type: 'danger',
        tag: '盘点差异',
        content: `${a.goods_name} 差异 ${a.diff_qty > 0 ? '+' : ''}${a.diff_qty}（${a.warehouse_name}）`
      }))
    ]
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.card-header {
  font-weight: bold;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
  padding: 20px 0;
}

.quick-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
