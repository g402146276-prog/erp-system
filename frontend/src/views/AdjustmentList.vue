<template>
  <div class="list-container">
    <div class="list-header">
      <h2>调整单列表</h2>
      <el-tag v-if="filter === 'pending'" type="warning">待审核</el-tag>
      <el-tag v-else-if="filter === 'applied'" type="success">已审核</el-tag>
    </div>

    <div class="filter-tabs">
      <el-button
        :type="filter === 'pending' ? 'primary' : 'default'"
        size="small"
        @click="filter = 'pending'; load()"
      >待审核</el-button>
      <el-button
        :type="filter === 'applied' ? 'primary' : 'default'"
        size="small"
        @click="filter = 'applied'; load()"
      >已审核</el-button>
      <el-button
        :type="filter === '' ? 'primary' : 'default'"
        size="small"
        @click="filter = ''; load()"
      >全部</el-button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-for="item in list" :key="item.id" class="adjust-card">
      <div class="adjust-top">
        <span class="adjust-no">{{ item.adjust_no }}</span>
        <el-tag :type="statusType(item.status)" size="small">{{ statusLabel(item.status) }}</el-tag>
      </div>
      <div class="adjust-body">
        <div class="adjust-goods">
          <strong>{{ item.goods_name }}</strong>
          <el-tag size="small">{{ item.goods_barcode }}</el-tag>
        </div>
        <div class="adjust-wh">{{ item.warehouse_name }}</div>
        <div class="adjust-qty">
          <span>系统: {{ item.system_qty }}</span>
          <span class="arrow">→</span>
          <span class="actual">实际: {{ item.actual_qty }}</span>
          <span class="diff" :class="{ up: item.diff_qty > 0, down: item.diff_qty < 0 }">
            ({{ item.diff_qty > 0 ? '+' : '' }}{{ item.diff_qty }})
          </span>
        </div>
        <div class="adjust-meta">
          <span>{{ item.operator }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
        <div v-if="item.remark" class="adjust-remark">备注: {{ item.remark }}</div>
      </div>
      <div class="adjust-actions" v-if="item.status === 'pending'">
        <el-button type="primary" size="small" @click="applyAdjust(item.id)">✅ 审核通过</el-button>
        <el-button type="danger" size="small" @click="cancelAdjust(item.id)">作废</el-button>
      </div>
    </div>

    <el-empty v-if="!loading && list.length === 0" description="暂无调整单" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adjustmentApi } from '../api/modules_ext'

const filter = ref('pending')
const list = ref([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    list.value = await adjustmentApi.list({ status: filter.value || undefined })
  } catch (_) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const applyAdjust = async (id) => {
  try {
    await adjustmentApi.apply(id)
    ElMessage.success('审核通过，库存已更新')
    load()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '审核失败')
  }
}

const cancelAdjust = async (id) => {
  try {
    await adjustmentApi.cancel(id)
    ElMessage.success('已作废')
    load()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '作废失败')
  }
}

const statusType = (s) => ({
  pending: 'warning',
  applied: 'success',
  cancelled: 'info',
  draft: 'default'
}[s] || 'default')

const statusLabel = (s) => ({
  pending: '待审核',
  applied: '已审核',
  cancelled: '已作废',
  draft: '草稿'
}[s] || s)

const formatDate = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN')
}

onMounted(load)
</script>

<style scoped>
.list-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}
.list-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.list-header h2 { margin: 0; }
.filter-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.loading { text-align: center; color: #909399; padding: 40px; }
.adjust-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.adjust-top { display: flex; justify-content: space-between; margin-bottom: 8px; }
.adjust-no { font-weight: bold; font-size: 14px; }
.adjust-goods { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.adjust-wh { color: #909399; font-size: 13px; margin-bottom: 4px; }
.adjust-qty { margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
.adjust-qty .arrow { color: #c0c4cc; }
.adjust-qty .actual { font-weight: bold; }
.adjust-qty .diff { font-weight: bold; }
.adjust-qty .diff.up { color: #67c23a; }
.adjust-qty .diff.down { color: #f56c6c; }
.adjust-meta { display: flex; gap: 16px; color: #c0c4cc; font-size: 12px; }
.adjust-remark { color: #909399; font-size: 13px; margin-top: 4px; }
.adjust-actions { display: flex; gap: 8px; margin-top: 12px; }
</style>
