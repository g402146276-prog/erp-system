<template>
  <div style="font-size:14px;color:#303133">

    <!-- ===== 页面标题 ===== -->
    <div style="font-size:20px;font-weight:600;color:#303133;margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid #409eff">采购入库单</div>

    <!-- ===== 单据抬头 ===== -->
    <div style="background:#f5f7fa;border:1px solid #e4e7ed;border-radius:6px;padding:16px 20px;margin-bottom:16px">
      <el-row :gutter="16">
        <el-col :span="6">
          <div style="margin-bottom:4px;font-size:14px;color:#606266">供应商</div>
          <el-select v-model="supplier_id" clearable placeholder="选择供应商" style="width:100%">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <div style="margin-bottom:4px;font-size:14px;color:#606266">入库仓库</div>
          <el-select v-model="warehouse_id" clearable placeholder="选择仓库" style="width:100%">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-col>
        <el-col :span="3">
          <div style="margin-bottom:4px;font-size:14px;color:#606266">经办人</div>
          <el-input :model-value="operator" disabled style="width:100%" />
        </el-col>
        <el-col :span="5">
          <div style="margin-bottom:4px;font-size:14px;color:#606266">备注</div>
          <el-input v-model="remark" placeholder="选填" style="width:100%" />
        </el-col>
        <el-col :span="5" style="display:flex;align-items:flex-end;gap:8px">
          <el-button type="primary" plain @click="showIntransitImport = true" style="flex:1">+ 从在途导入</el-button>
          <el-popover placement="bottom" trigger="click" :width="160">
            <template #reference>
              <el-button style="width:36px;font-size:16px;padding:0">☰</el-button>
            </template>
            <div style="padding:4px 0">
              <div style="font-size:13px;color:#909399;padding:4px 8px 8px">显示 / 隐藏列</div>
              <div v-for="col in columns" :key="col.id" v-show="!col.locked" style="padding:5px 8px;display:flex;align-items:center;gap:8px;cursor:pointer;border-radius:4px;hover:background:#f5f7fa" @click="toggleColumn(col)">
                <div :style="{width:16,height:16,borderRadius:3,border:'1px solid #dcdfe6',background:col.visible?'#409eff':'#fff',display:'flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:12,lineHeight:'16px',transition:'.2s'}">{{ col.visible ? '✓' : '' }}</div>
                <span style="font-size:13px;color:#303133">{{ col.label }}</span>
              </div>
            </div>
          </el-popover>
        </el-col>
      </el-row>
    </div>

    <!-- ===== 录入区域（可定制列） ===== -->
    <div style="border:1px solid #dcdfe6;border-radius:6px;margin-bottom:12px;overflow:hidden;user-select:none">
      <!-- 表头（可拖拽排序） -->
      <div :style="headerGridStyle" style="background:#ebeef5;border-bottom:1px solid #dcdfe6">
        <template v-for="col in visibleCols" :key="col.id">
          <div
            :style="{padding:'10px 10px',fontSize:'14px',color:'#303133',fontWeight:600,borderRight:'1px solid #dcdfe6',position:'relative',textAlign:col.align||'left',display:'flex',alignItems:'center',gap:4,cursor:'grab'}"
            draggable="true"
            @dragstart="onDragStart($event, col.id)"
            @dragover="onDragOver($event, col.id)"
            @dragend="onDragEnd"
            @drop.prevent="onDrop($event, col.id)"
          >
            <span>{{ col.label }}</span>
            <div v-if="col.resizable" style="position:absolute;right:0;top:0;bottom:0;width:5px;cursor:col-resize;z-index:2" @mousedown.prevent="startResize($event, col.id)" />
          </div>
        </template>
      </div>
      <!-- 输入行 -->
      <div :style="inputGridStyle" style="align-items:center;background:#fff">
        <template v-for="col in visibleCols" :key="col.id">
          <div :style="{borderRight:col.id!==visibleCols[visibleCols.length-1]?.id?'1px solid #dcdfe6':'none',height:36,display:'flex',alignItems:'center',padding:'0 6px',overflow:'hidden'}">
            <el-input v-if="col.id==='barcode'" v-model="entry.barcode" ref="barcodeRef" placeholder="扫码或输入" size="large" style="width:100%;height:36px" @change="onBarcodeChange" @keyup.enter="afterBarcode" />
            <el-autocomplete v-else-if="col.id==='goodsName'" v-model="entry.goodsName" :fetch-suggestions="searchGoods" :trigger-on-focus="false" placeholder="搜索选择商品" value-key="name" size="large" style="width:100%" @select="onGoodsSelect" @clear="entry.goodsId=null" clearable />
            <el-input-number v-else-if="col.id==='quantity'" v-model="entry.quantity" :min="1" :max="99999" size="large" style="width:100%" controls-position="right" />
            <el-input v-else-if="col.id==='bojunOrderNo'" v-model="entry.bojun_order_no" placeholder="伯俊单号" size="large" style="width:100%" />
            <el-input v-else-if="col.id==='remark'" v-model="entry.remark" placeholder="备注" size="large" style="width:100%" />
            <el-button v-else-if="col.id==='action'" type="primary" size="large" @click="addItem" :disabled="!entry.goodsId" style="width:100%;font-size:14px;padding:0;height:36px">添加</el-button>
          </div>
        </template>
      </div>
    </div>

    <!-- ===== 待入库明细 ===== -->
    <div v-if="pendingItems.length > 0" style="border:1px solid #dcdfe6;border-radius:6px;margin-bottom:12px;overflow:hidden">
      <div style="padding:10px 16px;background:#f5f7fa;border-bottom:1px solid #dcdfe6;display:flex;justify-content:space-between;align-items:center;font-size:14px;color:#303133;font-weight:600">
        <span>待入库明细（共 {{ pendingItems.length }} 项）</span>
        <span v-if="linkedIntransitNo" style="font-size:13px;color:#909399;font-weight:400">关联在途: {{ linkedIntransitNo }}</span>
      </div>
      <el-table :data="pendingItems" border stripe max-height="320" size="large" style="width:100%">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="barcode" label="条码" width="160" />
        <el-table-column prop="goodsName" label="品名" min-width="160" />
        <el-table-column prop="quantity" label="数量" width="80" header-align="center" align="center" />
        <el-table-column prop="bojun_order_no" label="伯俊单号" width="160" />
        <el-table-column prop="remark" label="备注" min-width="130" />
        <el-table-column label="操作" width="70" fixed="right" header-align="center" align="center">
          <template #default="{row,$index}">
            <el-button link type="danger" size="small" @click="pendingItems.splice($index,1)" style="font-size:14px">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="padding:10px 16px;border-top:1px solid #dcdfe6;display:flex;justify-content:flex-end;gap:10px;background:#fff">
        <el-button size="large" @click="clearAll" style="font-size:14px">清空全部</el-button>
        <el-button type="primary" size="large" @click="submitBatch" :loading="submitting" style="font-size:14px;font-weight:500">提交入库（{{ pendingItems.length }} 项）</el-button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else style="border:1px dashed #dcdfe6;border-radius:6px;padding:40px 0;text-align:center;background:#fafafa">
      <div style="font-size:40px;color:#c0c4cc;margin-bottom:10px">📋</div>
      <div style="font-size:14px;color:#909399">暂无待入库明细</div>
      <div style="font-size:13px;color:#c0c4cc;margin-top:4px">扫描条码添加商品，或搜索商品名称选择</div>
    </div>

    <!-- ===== 在途订单导入弹窗 ===== -->
    <el-dialog v-model="showIntransitImport" title="选择在途订单导入" width="760px" top="8vh">
      <el-table :data="intransitOrders" border stripe size="large" @row-click="selectIntransit" style="width:100%">
        <el-table-column width="50">
          <template #default="{row}">
            <el-radio :val="selectedIntransitId" :model-value="selectedIntransitId === row.id" @change="selectedIntransitId = row.id" />
          </template>
        </el-table-column>
        <el-table-column prop="apply_no" label="单号" width="150" />
        <el-table-column prop="goods_barcode" label="条码" width="130" />
        <el-table-column prop="goods_name" label="商品" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="70" header-align="center" align="center" />
        <el-table-column prop="bojun_order_no" label="伯俊单号" width="140" />
        <el-table-column label="类型" width="80">
          <template #default="{row}">{{ {direct_shipping:'直发',cross_transfer:'调拨'}[row.order_type] }}</template>
        </el-table-column>
      </el-table>
      <div v-if="!intransitOrders.length" style="text-align:center;padding:30px;color:#909399;font-size:14px">暂无待处理的在途订单</div>
      <template #footer>
        <el-button @click="showIntransitImport = false" size="large" style="font-size:14px">取消</el-button>
        <el-button type="primary" :disabled="!selectedIntransitId" @click="importFromIntransit" size="large" style="font-size:14px">导入明细</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { purchaseInboundApi, intransitOrderApi } from '../api/modules_ext'
import { goodsApi, warehouseApi, supplierApi } from '../api/modules'

// ===== 抬头 =====
const supplier_id = ref(null)
const warehouse_id = ref(null)
const remark = ref('')
const operator = ref(localStorage.getItem('erp_user') ? JSON.parse(localStorage.getItem('erp_user')).display_name : '')
const suppliers = ref([])
const warehouses = ref([])

// ===== 列定义 =====
const STORAGE_KEY = 'erp_purchase_inbound_cols'

// 列定义（默认配置）
const defaultColumns = [
  { id: 'barcode',       label: '条码',     width: 175, visible: true,  resizable: true,  locked: false, align: 'left' },
  { id: 'goodsName',     label: '商品名称', width: 280, visible: true,  resizable: true,  locked: true,  align: 'left' },
  { id: 'quantity',      label: '数量',     width: 115, visible: true,  resizable: true,  locked: false, align: 'center' },
  { id: 'bojunOrderNo',  label: '伯俊单号', width: 175, visible: true,  resizable: true,  locked: false, align: 'left' },
  { id: 'remark',        label: '备注',     width: 145, visible: true,  resizable: true,  locked: false, align: 'left' },
  { id: 'action',        label: '',         width: 90,  visible: true,  resizable: false, locked: true,  align: 'center' },
]

// 从 localStorage 恢复列配置
function loadColumns() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch { return null }
}

const saved = loadColumns()
const columns = reactive(
  (saved && saved.length === defaultColumns.length
    ? saved.map(s => {
        const def = defaultColumns.find(d => d.id === s.id)
        return { ...def, ...s }
      })
    : defaultColumns
  ).map(c => ({ ...c }))
)

const visibleCols = computed(() => columns.filter(c => c.visible))

function saveColumns() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(columns.map(c => ({
    id: c.id, width: c.width, visible: c.visible,
  }))))
}

const gridTemplate = computed(() =>
  visibleCols.value.map(c => c.width + 'px').join(' ')
)

const headerGridStyle = computed(() => ({
  display: 'grid',
  gridTemplateColumns: gridTemplate.value,
}))

const inputGridStyle = computed(() => ({
  display: 'grid',
  gridTemplateColumns: gridTemplate.value,
}))

// ---- 列宽拖拽 ----
const resizing = ref(null)
const resizeStartX = ref(0)
const resizeStartW = ref(0)

function startResize(e, colId) {
  resizing.value = colId
  resizeStartX.value = e.clientX
  const col = columns.find(c => c.id === colId)
  resizeStartW.value = col.width
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
}

function onResize(e) {
  if (!resizing.value) return
  const dx = e.clientX - resizeStartX.value
  const col = columns.find(c => c.id === resizing.value)
  const newW = Math.max(60, resizeStartW.value + dx)
  // 所有可见列必须能在一屏内显示，防止被挤出去
  const totalOther = columns
    .filter(c => c.visible && c.id !== resizing.value)
    .reduce((s, c) => s + c.width, 0)
  const maxAllowed = (window.innerWidth - 260) - totalOther
  col.width = Math.max(60, Math.min(newW, maxAllowed))
}

function stopResize() {
  resizing.value = null
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  saveColumns()
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
})

function toggleColumn(col) {
  col.visible = !col.visible
  saveColumns()
}

// ---- 列拖拽排序 ----
let draggedColId = null

function onDragStart(e, colId) {
  draggedColId = colId
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', colId)
}

function onDragOver(e) {
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
}

function onDrop(e, targetColId) {
  e.preventDefault()
  if (!draggedColId || draggedColId === targetColId) return
  const fromIdx = columns.findIndex(c => c.id === draggedColId)
  const toIdx = columns.findIndex(c => c.id === targetColId)
  if (fromIdx === -1 || toIdx === -1) return
  const [moved] = columns.splice(fromIdx, 1)
  columns.splice(toIdx, 0, moved)
  draggedColId = null
  saveColumns()
}

function onDragEnd() {
  draggedColId = null
}

// ===== 录入 =====
const barcodeRef = ref(null)
const entry = ref({ barcode: '', goodsId: null, goodsName: '', quantity: 1, bojun_order_no: '', remark: '' })
const pendingItems = ref([])
const submitting = ref(false)

// ===== 在途导入 =====
const showIntransitImport = ref(false)
const intransitOrders = ref([])
const selectedIntransitId = ref(null)
const linkedIntransitId = ref(null)
const linkedIntransitNo = ref('')

// ---- 条码录入 ----
async function onBarcodeChange() {
  if (!entry.value.barcode) { entry.value.goodsId = null; entry.value.goodsName = ''; return }
  try {
    const g = await goodsApi.getByBarcode(entry.value.barcode)
    entry.value.goodsId = g.id
    entry.value.goodsName = g.name
  } catch {
    entry.value.goodsId = null
    entry.value.goodsName = ''
  }
}

function afterBarcode() {
  if (entry.value.goodsName) addItem()
  else if (entry.value.barcode) onBarcodeChange()
}

// ---- 商品名自动搜索 ----
async function searchGoods(queryStr, cb) {
  if (!queryStr || queryStr.length < 1) { cb([]); return }
  try {
    const list = await goodsApi.list({ keyword: queryStr, limit: 15 })
    cb(list.map(g => ({ ...g, value: `${g.name} (${g.barcode})` })))
  } catch { cb([]) }
}

function onGoodsSelect(item) {
  entry.value.goodsId = item.id
  entry.value.barcode = item.barcode
  entry.value.goodsName = item.name
  nextTick(() => barcodeRef.value?.focus())
}

// ---- 添加明细 ----
function addItem() {
  if (!entry.value.goodsId) { ElMessage.warning('未选择商品'); return }
  if (!entry.value.bojun_order_no) { ElMessage.warning('请输入伯俊单号'); return }
  pendingItems.value.push({
    goodsId: entry.value.goodsId,
    barcode: entry.value.barcode,
    goodsName: entry.value.goodsName,
    quantity: entry.value.quantity,
    bojun_order_no: entry.value.bojun_order_no,
    remark: entry.value.remark || '',
  })
  resetEntry()
}

function resetEntry() {
  entry.value = { barcode: '', goodsId: null, goodsName: '', quantity: 1, bojun_order_no: '', remark: '' }
  nextTick(() => barcodeRef.value?.focus())
}

function clearAll() {
  pendingItems.value = []
  linkedIntransitId.value = null
  linkedIntransitNo.value = ''
  resetEntry()
}

// ---- 批量提交 ----
async function submitBatch() {
  if (!warehouse_id.value) { ElMessage.warning('请选择仓库'); return }
  if (pendingItems.value.length === 0) return
  submitting.value = true
  try {
    const payload = {
      warehouse_id: warehouse_id.value,
      items: pendingItems.value.map(i => ({
        goods_id: i.goodsId,
        received_quantity: i.quantity,
        bojun_order_no: i.bojun_order_no,
        remark: i.remark,
      })),
    }
    if (linkedIntransitId.value) payload.intransit_order_id = linkedIntransitId.value
    await purchaseInboundApi.batchCreate(payload)
    ElMessage.success(`入库完成，共 ${pendingItems.value.length} 项`)
    pendingItems.value = []
    linkedIntransitId.value = null
    linkedIntransitNo.value = ''
    resetEntry()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '入库失败')
  } finally {
    submitting.value = false
  }
}

// ---- 在途订单导入 ----
async function loadIntransitOrders() {
  intransitOrders.value = await intransitOrderApi.list({ status: 'pending' })
}

function selectIntransit(row) {
  selectedIntransitId.value = selectedIntransitId.value === row.id ? null : row.id
}

async function importFromIntransit() {
  if (!selectedIntransitId.value) return
  try {
    const order = await intransitOrderApi.get(selectedIntransitId.value)
    pendingItems.value.push({
      goodsId: order.goods_id,
      barcode: order.goods_barcode || '',
      goodsName: order.goods_name,
      quantity: order.quantity,
      bojun_order_no: order.bojun_order_no || '',
      remark: `在途:${order.apply_no}` + (order.remark ? ` ${order.remark}` : ''),
    })
    linkedIntransitId.value = order.id
    linkedIntransitNo.value = order.apply_no
    ElMessage.success(`已导入: ${order.goods_name} x${order.quantity}`)
    showIntransitImport.value = false
    selectedIntransitId.value = null
  } catch (e) {
    ElMessage.error('导入失败: ' + (e?.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  suppliers.value = await supplierApi.list()
  warehouses.value = await warehouseApi.list()
  nextTick(() => barcodeRef.value?.focus())
})
</script>
