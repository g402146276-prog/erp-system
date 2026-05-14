<template>
  <div class="scan-container">
    <div class="scan-header">
      <h2>扫码查货</h2>
      <p class="scan-hint">对准商品条码，自动识别</p>
    </div>

    <div class="scanner-wrapper" v-show="!scanResult">
      <div id="scanner" ref="scannerRef"></div>
      <div class="scanner-overlay">
        <div class="scan-frame"></div>
      </div>
      <div class="manual-input">
        <el-input
          v-model="manualBarcode"
          placeholder="或手动输入条码"
          size="large"
          @keyup.enter="searchByBarcode"
        >
          <template #append>
            <el-button @click="searchByBarcode">查询</el-button>
          </template>
        </el-input>
      </div>
    </div>

    <div v-if="scanResult" class="scan-result">
      <div class="result-card">
        <div class="result-header">
          <h3>{{ scanResult.name }}</h3>
          <el-tag>{{ scanResult.barcode }}</el-tag>
        </div>
        <p class="spec" v-if="scanResult.spec">规格: {{ scanResult.spec }}</p>
        <p class="price" v-if="scanResult.price">单价: ¥{{ scanResult.price }}</p>

        <div class="stock-list">
          <div
            v-for="ws in scanResult.warehouse_stocks"
            :key="ws.warehouse_id"
            class="stock-item"
            :class="{ highlight: selectedWh === ws.warehouse_id }"
            @click="selectWarehouse(ws)"
          >
            <div class="stock-header">
              <span class="wh-name">{{ ws.warehouse_name }}</span>
              <el-tag type="primary" class="qty-tag">{{ ws.quantity }}</el-tag>
            </div>
            <div v-if="ws.locations && ws.locations.length" class="location-list">
              <el-tag
                v-for="loc in ws.locations"
                :key="loc.code"
                size="small"
                type="info"
                class="loc-tag"
              >
                {{ loc.code }}: {{ loc.quantity }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <el-button type="warning" size="large" @click="goAdjust">
          📌 快速盘点
        </el-button>
        <el-button type="primary" size="large" @click="goDetail">
          查看详情
        </el-button>
        <el-button size="large" @click="rescan">
          🔄 重新扫码
        </el-button>
      </div>

      <div class="recent-records" v-if="recentRecords.length">
        <h4>最近记录</h4>
        <div v-for="r in recentRecords.slice(0, 5)" :key="r.date" class="record-item">
          <span class="record-type">{{ r.type }}</span>
          <span class="record-detail">{{ r.detail }}</span>
          <span class="record-date">{{ formatDate(r.date) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Html5Qrcode } from 'html5-qrcode'
import { locationApi, stockApiExt } from '../api/modules_ext'

const router = useRouter()
const scannerRef = ref(null)
const manualBarcode = ref('')
const scanResult = ref(null)
const recentRecords = ref([])
const selectedWh = ref(null)
const selectedWhData = ref(null)

let html5QrCode = null

const startScanner = async () => {
  try {
    html5QrCode = new Html5Qrcode("scanner")
    await html5QrCode.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 250, height: 150 } },
      onScanSuccess
    )
  } catch (err) {
    console.error('Camera error:', err)
    ElMessage.warning('无法启动摄像头，请手动输入条码')
  }
}

const onScanSuccess = (decodedText) => {
  if (html5QrCode) {
    html5QrCode.stop()
  }
  manualBarcode.value = decodedText
  searchByBarcode()
}

const searchByBarcode = async () => {
  if (!manualBarcode.value) {
    ElMessage.warning('请输入条码')
    return
  }
  try {
    const res = await locationApi.scan(manualBarcode.value)
    scanResult.value = res
    // Also get recent records
    try {
      const detail = await stockApiExt.detail(res.goods_id)
      recentRecords.value = detail.recent_records || []
    } catch (_) {}
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '未找到该商品')
  }
}

const selectWarehouse = (ws) => {
  selectedWh.value = ws.warehouse_id
  selectedWhData.value = ws
}

const goAdjust = () => {
  if (!scanResult.value) return
  router.push({
    path: '/quick-adjust',
    query: {
      goods_id: scanResult.value.goods_id,
      barcode: scanResult.value.barcode,
      goods_name: scanResult.value.name,
      warehouse_id: selectedWh.value || scanResult.value.warehouse_stocks[0]?.warehouse_id,
      warehouse_name: selectedWhData.value?.warehouse_name || scanResult.value.warehouse_stocks[0]?.warehouse_name,
      system_qty: selectedWhData.value?.quantity || scanResult.value.warehouse_stocks[0]?.quantity
    }
  })
}

const goDetail = () => {
  if (!scanResult.value) return
  router.push(`/goods-detail/${scanResult.value.goods_id}`)
}

const rescan = () => {
  scanResult.value = null
  recentRecords.value = []
  selectedWh.value = null
  manualBarcode.value = ''
  startScanner()
}

const formatDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  startScanner()
})

onUnmounted(() => {
  if (html5QrCode) {
    html5QrCode.stop().catch(() => {})
  }
})
</script>

<style scoped>
.scan-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}
.scan-header {
  text-align: center;
  margin-bottom: 20px;
}
.scan-header h2 { margin: 0 0 4px; color: #303133; }
.scan-hint { margin: 0; color: #909399; font-size: 14px; }
.scanner-wrapper {
  position: relative;
  margin-bottom: 20px;
}
#scanner {
  width: 100%;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}
.scanner-overlay {
  display: none;
}
.manual-input {
  margin-top: 12px;
}
.scan-result {
  margin-top: 16px;
}
.result-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 16px;
}
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.result-header h3 { margin: 0; font-size: 20px; }
.spec, .price { margin: 4px 0; color: #606266; font-size: 14px; }
.stock-list { margin-top: 16px; }
.stock-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.stock-item:hover, .stock-item.highlight {
  border-color: #409EFF;
  background: #ecf5ff;
}
.stock-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.wh-name { font-weight: bold; }
.qty-tag { font-size: 16px; }
.location-list {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.loc-tag {
  font-size: 12px;
}
.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.action-buttons .el-button { flex: 1; }
.recent-records {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.recent-records h4 { margin: 0 0 12px; }
.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.record-item:last-child { border-bottom: none; }
.record-type {
  background: #f0f5ff;
  color: #409EFF;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}
.record-detail { flex: 1; color: #303133; }
.record-date { color: #c0c4cc; font-size: 12px; }
</style>
