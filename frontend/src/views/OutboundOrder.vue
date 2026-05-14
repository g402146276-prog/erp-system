<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>出库单</h2>
      <el-button type="primary" @click="showCreate=true">新建出库单</el-button>
    </div>
    <el-alert title="销售出库=算业绩；其他出库=其他领用。出库未取的货在「暂存仓库」状态，伯俊出库后更新状态。" type="info" :closable="false" show-icon style="margin:12px 0" />
    <el-form :inline="true" style="margin-bottom:8px">
      <el-form-item label="类型">
        <el-select v-model="filters.order_type" clearable placeholder="全部" @change="load">
          <el-option label="销售出库" value="sales" />
          <el-option label="其他出库" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="提货状态">
        <el-select v-model="filters.pickup_status" clearable placeholder="全部" @change="load">
          <el-option label="已提走" value="picked_up" />
          <el-option label="暂存仓库" value="stored" />
        </el-select>
      </el-form-item>
      <el-form-item label="伯俊状态">
        <el-select v-model="filters.bojun_status" clearable placeholder="全部" @change="load">
          <el-option label="已出库" value="outbound" />
          <el-option label="待核销" value="pending" />
          <el-option label="未知" value="unknown" />
        </el-select>
      </el-form-item>
    </el-form>
    <el-table :data="list" border stripe>
      <el-table-column prop="outbound_no" label="单号" width="150" />
      <el-table-column label="类型" width="90">
        <template #default="{row}">{{ {sales:'销售出库',gift:'赠送',other:'其他'}[row.order_type] }}</template>
      </el-table-column>
      <el-table-column prop="goods_barcode" label="条码" width="120" />
      <el-table-column prop="goods_name" label="商品" min-width="150" />
      <el-table-column prop="quantity" label="数量" width="70" />
      <el-table-column prop="warehouse_name" label="仓库" width="100" />
      <el-table-column label="提货状态" width="100">
        <template #default="{row}">
          <el-tag :type="row.pickup_status==='stored'?'warning':'success'">
            {{ {picked_up:'已提走',stored:'暂存仓库'}[row.pickup_status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="伯俊状态" width="100">
        <template #default="{row}">
          <el-tag :type="{outbound:'success',pending:'warning',unknown:'info'}[row.bojun_status]" size="small">
            {{ {outbound:'已出库',pending:'待核销',unknown:'未知'}[row.bojun_status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="operator" label="操作人" width="80" />
      <el-table-column prop="created_at" label="时间" width="150" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{row}">
          <el-select v-model="row.bojun_status" size="small" @change="updateStatus(row)" style="width:90px">
            <el-option label="未知" value="unknown" />
            <el-option label="待核销" value="pending" />
            <el-option label="已出库" value="outbound" />
          </el-select>
          <el-button size="small" type="danger" @click="reverseOrder(row)">红冲</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建出库单" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="出库类型">
          <el-radio-group v-model="form.order_type">
            <el-radio value="sales">销售出库</el-radio>
            <el-radio value="other">其他出库</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="商品条码">
          <el-input v-model="barcode" placeholder="扫码输入" @change="loadGoods" style="width:200px" />
          <span style="margin-left:8px;color:#999">{{ goodsName }}</span>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="form.warehouse_id" filterable>
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="提货状态">
          <el-radio-group v-model="form.pickup_status">
            <el-radio value="picked_up">已提走</el-radio>
            <el-radio value="stored">暂存仓库（出库未取）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="伯俊状态">
          <el-select v-model="form.bojun_status">
            <el-option label="未知" value="unknown" />
            <el-option label="待核销" value="pending" />
            <el-option label="已出库" value="outbound" />
          </el-select>
        </el-form-item>
        <el-form-item label="销售人员" v-if="form.order_type==='sales'">
          <el-select v-model="form.salesperson_id" filterable clearable>
            <el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" @click="createOutbound">确认出库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { outboundApi } from '../api/modules_ext'
import { goodsApi, warehouseApi } from '../api/modules'

const list = ref([])
const showCreate = ref(false)
const barcode = ref('')
const goodsName = ref('')
const goodsId = ref(null)
const warehouses = ref([])
const users = ref([])
const filters = ref({ order_type: '', pickup_status: '', bojun_status: '' })
const form = ref({
  order_type: 'sales', quantity: 1, warehouse_id: null,
  pickup_status: 'picked_up', bojun_status: 'unknown',
  salesperson_id: null, remark: '',
})

async function load() {
  const params = {}
  if (filters.value.order_type) params.order_type = filters.value.order_type
  if (filters.value.pickup_status) params.pickup_status = filters.value.pickup_status
  if (filters.value.bojun_status) params.bojun_status = filters.value.bojun_status
  list.value = await outboundApi.list(params)
}

async function loadGoods() {
  if (!barcode.value) return
  try {
    const g = await goodsApi.getByBarcode(barcode.value)
    goodsId.value = g.id
    goodsName.value = g.name
  } catch { goodsName.value = '未找到' }
}

async function createOutbound() {
  if (!goodsId.value || !form.value.warehouse_id) return
  await outboundApi.create({
    order_type: form.value.order_type,
    goods_id: goodsId.value,
    quantity: form.value.quantity,
    warehouse_id: form.value.warehouse_id,
    pickup_status: form.value.pickup_status,
    bojun_status: form.value.bojun_status,
    salesperson_id: form.value.salesperson_id,
    remark: form.value.remark,
  })
  showCreate.value = false
  form.value = { order_type: 'sales', quantity: 1, warehouse_id: null, pickup_status: 'picked_up', bojun_status: 'unknown', salesperson_id: null, remark: '' }
  barcode.value = ''
  goodsName.value = ''
  goodsId.value = null
  await load()
}

async function updateStatus(row) {
  await outboundApi.update(row.id, { bojun_status: row.bojun_status })
}

async function reverseOrder(row) {
  await outboundApi.reverse(row.id)
  await load()
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  await load()
})
</script>
