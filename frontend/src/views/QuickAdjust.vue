<template>
  <div class="adjust-container">
    <div class="adjust-header">
      <el-button text @click="goBack">← 返回</el-button>
      <h2>快速盘点</h2>
    </div>

    <el-card class="goods-card">
      <div class="goods-info">
        <h3>{{ goodsName }}</h3>
        <el-tag>{{ barcode }}</el-tag>
      </div>
      <div class="warehouse-info">
        <span class="label">仓库:</span>
        <span class="value">{{ warehouseName }}</span>
      </div>
      <div class="qty-row">
        <span class="label">系统记录:</span>
        <span class="value system-qty">{{ systemQty }}</span>
      </div>

      <el-divider />

      <div class="actual-row">
        <label class="label">实际清点数量:</label>
        <el-input-number
          v-model="actualQty"
          :min="0"
          size="large"
          controls-position="right"
          style="width: 100%"
        />
      </div>

      <div class="diff-info" v-if="actualQty !== systemQty">
        <el-alert
          :title="`差异: ${actualQty - systemQty} 个`"
          :type="actualQty > systemQty ? 'success' : 'warning'"
          show-icon
        />
      </div>

      <el-form-item label="备注" style="margin-top: 12px">
        <el-input
          v-model="remark"
          type="textarea"
          :rows="2"
          placeholder="如有特殊情况请备注"
        />
      </el-form-item>
    </el-card>

    <div class="action-tip" v-if="actualQty !== systemQty">
      <p>⚠️ 提交后只创建调整单，<strong>不会修改库存</strong>，需主管审核后才生效</p>
    </div>

    <el-button
      type="primary"
      size="large"
      :loading="submitting"
      :disabled="actualQty === systemQty"
      style="width: 100%"
      @click="submitAdjust"
    >
      📌 提交调整单
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adjustmentApi } from '../api/modules_ext'

const route = useRoute()
const router = useRouter()

const goodsId = ref(parseInt(route.query.goods_id))
const barcode = ref(route.query.barcode || '')
const goodsName = ref(route.query.goods_name || '')
const warehouseId = ref(parseInt(route.query.warehouse_id))
const warehouseName = ref(route.query.warehouse_name || '')
const systemQty = ref(parseInt(route.query.system_qty) || 0)
const actualQty = ref(systemQty.value)
const remark = ref('')
const submitting = ref(false)

const goBack = () => router.back()

const submitAdjust = async () => {
  submitting.value = true
  try {
    await adjustmentApi.create({
      warehouse_id: warehouseId.value,
      goods_id: goodsId.value,
      actual_qty: actualQty.value,
      remark: remark.value
    })
    ElMessage.success('调整单已提交，等待审核')
    router.push('/adjustment-list')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.adjust-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}
.adjust-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.adjust-header h2 { margin: 0; }
.goods-card { margin-bottom: 16px; }
.goods-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.goods-info h3 { margin: 0; font-size: 20px; }
.warehouse-info, .qty-row {
  margin-bottom: 8px;
}
.label { color: #909399; margin-right: 8px; }
.value.system-qty { font-size: 24px; font-weight: bold; color: #409EFF; }
.actual-row { margin-bottom: 12px; }
.diff-info { margin: 12px 0; }
.action-tip {
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}
.action-tip p { margin: 0; color: #e6a23c; font-size: 14px; }
</style>
