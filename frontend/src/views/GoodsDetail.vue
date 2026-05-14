<template>
  <div class="detail-container">
    <div class="detail-header">
      <el-button text @click="goBack">← 返回</el-button>
      <h2>{{ goods.name }}</h2>
    </div>

    <el-card class="info-card" v-if="goods.goods_id">
      <div class="goods-basic">
        <div class="goods-field"><label>条码</label><span>{{ goods.barcode }}</span></div>
        <div class="goods-field"><label>规格</label><span>{{ goods.spec || '-' }}</span></div>
        <div class="goods-field"><label>单位</label><span>{{ goods.unit || '-' }}</span></div>
        <div class="goods-field"><label>单价</label><span>¥{{ goods.price || 0 }}</span></div>
      </div>

      <el-divider />

      <h4>库存分布</h4>
      <div v-for="ws in goods.warehouse_stocks" :key="ws.warehouse_id" class="stock-row">
        <div class="stock-row-header">
          <span class="wh-name">{{ ws.warehouse_name }}</span>
          <el-tag type="primary" size="large">{{ ws.quantity }}</el-tag>
        </div>
        <div v-if="ws.locations && ws.locations.length" class="locs">
          <el-tag v-for="loc in ws.locations" :key="loc.code" size="small" type="info">
            {{ loc.code }}: {{ loc.quantity }}
          </el-tag>
        </div>
        <div class="stock-actions">
          <el-button size="small" type="warning" @click="goQuickAdjust(ws)">
            📌 盘点此仓
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="records-card" v-if="goods.recent_records && goods.recent_records.length">
      <template #header><span>最近业务记录</span></template>
      <div v-for="r in goods.recent_records" :key="r.date" class="record-item">
        <div class="record-left">
          <span class="record-type" :class="r.type">{{ r.type }}</span>
        </div>
        <div class="record-mid">
          <span class="record-detail">{{ r.detail }}</span>
          <span class="record-warehouse">{{ r.warehouse }}</span>
        </div>
        <div class="record-right">
          <span class="record-date">{{ formatDate(r.date) }}</span>
          <span class="record-operator">{{ r.operator }}</span>
        </div>
      </div>
    </el-card>

    <el-empty v-if="loading" description="加载中..." />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stockApiExt } from '../api/modules_ext'

const route = useRoute()
const router = useRouter()
const goods = ref({})
const loading = ref(true)

const goBack = () => router.back()

const goQuickAdjust = (ws) => {
  router.push({
    path: '/quick-adjust',
    query: {
      goods_id: goods.value.goods_id,
      barcode: goods.value.barcode,
      goods_name: goods.value.name,
      warehouse_id: ws.warehouse_id,
      warehouse_name: ws.warehouse_name,
      system_qty: ws.quantity
    }
  })
}

const formatDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2,'0')}`
}

onMounted(async () => {
  const id = route.params.id
  try {
    goods.value = await stockApiExt.detail(id)
  } catch (err) {
    ElMessage.error('加载商品详情失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-header h2 { margin: 0; font-size: 20px; }
.info-card { margin-bottom: 16px; }
.goods-basic { display: grid; gap: 8px; }
.goods-field { display: flex; gap: 12px; }
.goods-field label { color: #909399; width: 60px; flex-shrink: 0; }
.stock-row {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 8px;
}
.stock-row-header { display: flex; justify-content: space-between; align-items: center; }
.wh-name { font-weight: bold; }
.locs { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
.stock-actions { margin-top: 8px; }
.records-card { margin-bottom: 16px; }
.record-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.record-item:last-child { border-bottom: none; }
.record-left { flex-shrink: 0; }
.record-type {
  background: #f0f5ff;
  color: #409EFF;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.record-type.入库 { background: #f0f9eb; color: #67c23a; }
.record-type.借出 { background: #fdf6ec; color: #e6a23c; }
.record-type.还货 { background: #f0f9eb; color: #67c23a; }
.record-type.盘点调整 { background: #fef0f0; color: #f56c6c; }
.record-mid { flex: 1; }
.record-mid .record-detail { display: block; }
.record-mid .record-warehouse { color: #909399; font-size: 12px; }
.record-right { text-align: right; flex-shrink: 0; }
.record-date { display: block; color: #c0c4cc; font-size: 12px; }
.record-operator { color: #909399; font-size: 12px; }
</style>
