<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>在途订单</h2>
      <el-button type="primary" @click="showCreate=true">新建在途订单</el-button>
    </div>
    <el-alert title="记录直发客户/跨店调拨的途中货物，创建即入库（算实物库存），后续关联调拨→出库完成链路。" type="warning" :closable="false" show-icon style="margin:12px 0" />
    <el-tabs v-model="tab">
      <el-tab-pane label="待处理" name="pending" />
      <el-tab-pane label="已完成" name="completed" />
      <el-tab-pane label="全部" name="all" />
    </el-tabs>
    <el-table :data="list" border stripe>
      <el-table-column prop="apply_no" label="单号" width="150" />
      <el-table-column label="类型" width="100">
        <template #default="{row}">{{ {direct_shipping:'直发客户',cross_transfer:'跨店调拨'}[row.order_type] }}</template>
      </el-table-column>
      <el-table-column prop="goods_barcode" label="条码" width="130" />
      <el-table-column prop="goods_name" label="商品" min-width="160" />
      <el-table-column prop="quantity" label="数量" width="70" />
      <el-table-column prop="customer_name" label="客户" width="120" />
      <el-table-column prop="bojun_order_no" label="伯俊单号" width="150" />
      <el-table-column label="状态" width="80">
        <template #default="{row}">
          <el-tag :type="{pending:'warning',completed:'success',cancelled:'info'}[row.status]">
            {{ {pending:'在途',completed:'已完成',cancelled:'已作废'}[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="160" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{row}">
          <el-button v-if="row.status==='pending'" size="small" type="danger" @click="cancel(row)">作废</el-button>
          <span v-else>-</span>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建在途订单" width="500px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="类型">
          <el-radio-group v-model="form.order_type">
            <el-radio value="direct_shipping">直发客户</el-radio>
            <el-radio value="cross_transfer">跨店调拨</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="商品条码">
          <el-input v-model="barcode" placeholder="扫码输入" @change="loadGoods" style="width:200px" />
          <span style="margin-left:8px;color:#999">{{ goodsName }}</span>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
        <el-form-item label="入库仓库">
          <el-select v-model="form.warehouse_id">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户名称" v-if="form.order_type==='direct_shipping'"><el-input v-model="form.customer_name" /></el-form-item>
        <el-form-item label="伯俊单号"><el-input v-model="form.bojun_order_no" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" @click="createOrder">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { intransitOrderApi } from '../api/modules_ext'
import { goodsApi, warehouseApi } from '../api/modules'

const list = ref([])
const tab = ref('pending')
const showCreate = ref(false)
const barcode = ref('')
const goodsName = ref('')
const goodsId = ref(null)
const warehouses = ref([])
const form = ref({
  order_type: 'direct_shipping', quantity: 1,
  warehouse_id: null, customer_name: '', bojun_order_no: '', remark: '',
})

async function load() {
  const params = {}
  if (tab.value !== 'all') params.status = tab.value
  list.value = await intransitOrderApi.list(params)
}

watch(tab, load)

async function loadGoods() {
  if (!barcode.value) return
  try {
    const g = await goodsApi.getByBarcode(barcode.value)
    goodsId.value = g.id
    goodsName.value = g.name
  } catch { goodsName.value = '未找到' }
}

async function createOrder() {
  if (!goodsId.value || !form.value.warehouse_id) return
  await intransitOrderApi.create({
    order_type: form.value.order_type,
    goods_id: goodsId.value,
    quantity: form.value.quantity,
    warehouse_id: form.value.warehouse_id,
    customer_name: form.value.customer_name,
    bojun_order_no: form.value.bojun_order_no,
    remark: form.value.remark,
  })
  showCreate.value = false
  form.value = { order_type: 'direct_shipping', quantity: 1, warehouse_id: null, customer_name: '', bojun_order_no: '', remark: '' }
  barcode.value = ''
  goodsName.value = ''
  goodsId.value = null
  await load()
}

async function cancel(row) {
  await intransitOrderApi.cancel(row.id)
  await load()
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  await load()
})
</script>
