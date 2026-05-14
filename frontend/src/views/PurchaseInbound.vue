<template>
  <div>
    <h2>采购入库</h2>
    <el-alert title="记录总仓来货，关联伯俊单号。同一单多次到货自动累加。" type="info" :closable="false" show-icon style="margin-bottom:12px" />

    <el-card style="margin-bottom:16px">
      <template #header>新增入库记录</template>
      <el-form :model="form" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="商品条码">
              <el-input v-model="barcode" placeholder="扫码输入" @change="loadGoods" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="商品名称">
              <span>{{ goodsName || '（扫码后自动填充）' }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="入库仓库">
              <el-select v-model="form.warehouse_id" placeholder="请选择仓库" clearable style="width:100%">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="入库数量">
              <el-input-number v-model="form.received_quantity" :min="1" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="伯俊单号">
              <el-input v-model="form.bojun_order_no" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="备注">
              <el-input v-model="form.remark" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="submit">确认入库</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <span>入库记录</span>
        <el-select v-model="summaryBojun" clearable placeholder="按伯俊单号筛选" style="margin-left:16px;width:200px" @change="loadRecords">
          <el-option v-for="s in summaries" :key="s.bojun_order_no" :label="s.bojun_order_no" :value="s.bojun_order_no" />
        </el-select>
      </template>
      <el-table :data="records" border stripe>
        <el-table-column prop="bojun_order_no" label="伯俊单号" width="150" />
        <el-table-column prop="goods_barcode" label="条码" width="130" />
        <el-table-column prop="goods_name" label="商品" min-width="160" />
        <el-table-column prop="received_quantity" label="数量" width="70" />
        <el-table-column prop="operator" label="操作人" width="80" />
        <el-table-column prop="remark" label="备注" min-width="120" />
        <el-table-column prop="created_at" label="时间" width="160" />
      </el-table>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header>按伯俊单号汇总</template>
      <el-table :data="summaries" border stripe>
        <el-table-column prop="bojun_order_no" label="伯俊单号" width="160" />
        <el-table-column prop="goods_name" label="商品" min-width="160" />
        <el-table-column prop="total_received" label="已收总数" width="100" header-align="center" align="center">
          <template #default="{row}"><strong>{{ row.total_received }}</strong></template>
        </el-table-column>
        <el-table-column prop="times" label="到货次数" width="80" header-align="center" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { purchaseInboundApi } from '../api/modules_ext'
import { goodsApi, warehouseApi } from '../api/modules'

const form = ref({ received_quantity: 1, warehouse_id: null, bojun_order_no: '', remark: '' })
const barcode = ref('')
const goodsName = ref('')
const goodsId = ref(null)
const warehouses = ref([])
const records = ref([])
const summaries = ref([])
const summaryBojun = ref('')

async function loadGoods() {
  if (!barcode.value) return
  try {
    const g = await goodsApi.getByBarcode(barcode.value)
    goodsId.value = g.id
    goodsName.value = g.name
  } catch { goodsName.value = '未找到' }
}

async function submit() {
  if (!goodsId.value || !form.value.warehouse_id) return
  await purchaseInboundApi.create({
    bojun_order_no: form.value.bojun_order_no,
    goods_id: goodsId.value,
    received_quantity: form.value.received_quantity,
    warehouse_id: form.value.warehouse_id,
    remark: form.value.remark,
  })
  form.value = { received_quantity: 1, warehouse_id: form.value.warehouse_id, bojun_order_no: '', remark: '' }
  barcode.value = ''
  goodsName.value = ''
  goodsId.value = null
  await loadRecords()
  await loadSummary()
}

async function loadRecords() {
  const params = {}
  if (summaryBojun.value) params.bojun_order_no = summaryBojun.value
  records.value = await purchaseInboundApi.list(params)
}

async function loadSummary() {
  summaries.value = await purchaseInboundApi.summary()
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  await loadRecords()
  await loadSummary()
})
</script>
