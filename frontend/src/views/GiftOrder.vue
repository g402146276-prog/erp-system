<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>赠送单</h2>
      <el-button type="primary" @click="showCreate=true">新建赠送单</el-button>
    </div>
    <el-alert title="赠送单本质是出库单（类型=赠送），货已送出但可能伯俊未出库。待伯俊出库后更新状态即可对齐。" type="info" :closable="false" show-icon style="margin:12px 0" />
    <el-tabs v-model="tab" style="margin-top:8px">
      <el-tab-pane label="全部" name="all" />
      <el-tab-pane label="待核销(伯俊未出库)" name="pending" />
      <el-tab-pane label="已核销" name="synced" />
    </el-tabs>
    <el-table :data="list" border stripe>
      <el-table-column prop="outbound_no" label="单号" width="160" />
      <el-table-column prop="goods_barcode" label="条码" width="130" />
      <el-table-column prop="goods_name" label="商品" min-width="160" />
      <el-table-column prop="quantity" label="数量" width="70" />
      <el-table-column prop="gift_recipient" label="受赠人" width="120" />
      <el-table-column label="伯俊状态" width="120">
        <template #default="{row}">
          <el-tag :type="{outbound:'success',pending:'warning',unknown:'info'}[row.bojun_status]">
            {{ {outbound:'已出库',pending:'待核销',unknown:'未知'}[row.bojun_status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="提货状态" width="100">
        <template #default="{row}">
          {{ {picked_up:'已提走',stored:'暂存仓库'}[row.pickup_status] }}
        </template>
      </el-table-column>
      <el-table-column prop="operator" label="操作人" width="80" />
      <el-table-column prop="created_at" label="时间" width="160" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{row}">
          <el-select v-model="row.bojun_status" size="small" @change="updateStatus(row)" style="width:90px">
            <el-option label="未知" value="unknown" />
            <el-option label="待核销" value="pending" />
            <el-option label="已出库" value="outbound" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建赠送单" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品条码">
          <el-input v-model="barcode" placeholder="扫码输入" @change="loadGoods" style="width:200px" />
          <span style="margin-left:8px;color:#999">{{ goodsName }}</span>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="form.warehouse_id">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="受赠人"><el-input v-model="form.gift_recipient" /></el-form-item>
        <el-form-item label="伯俊状态">
          <el-select v-model="form.bojun_status">
            <el-option label="未知" value="unknown" />
            <el-option label="待核销" value="pending" />
          </el-select>
        </el-form-item>
        <el-form-item label="提货状态">
          <el-radio-group v-model="form.pickup_status">
            <el-radio label="picked_up">已提走</el-radio>
            <el-radio label="stored">暂存仓库</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" @click="createGift">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { giftApi, outboundApi } from '../api/modules_ext'
import { goodsApi, warehouseApi } from '../api/modules'

const list = ref([])
const tab = ref('all')
const showCreate = ref(false)
const barcode = ref('')
const goodsName = ref('')
const goodsId = ref(null)
const warehouses = ref([])
const form = ref({
  quantity: 1, warehouse_id: null, gift_recipient: '',
  bojun_status: 'pending', pickup_status: 'picked_up', remark: '',
})

async function load() {
  const params = {}
  if (tab.value === 'pending') params.bojun_status = 'pending'
  if (tab.value === 'synced') params.bojun_status = 'outbound'
  list.value = await giftApi.list(params)
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

async function createGift() {
  if (!goodsId.value) return
  await outboundApi.create({
    order_type: 'gift',
    goods_id: goodsId.value,
    quantity: form.value.quantity,
    warehouse_id: form.value.warehouse_id,
    gift_recipient: form.value.gift_recipient,
    bojun_status: form.value.bojun_status,
    pickup_status: form.value.pickup_status,
    remark: form.value.remark,
  })
  showCreate.value = false
  form.value = { quantity: 1, warehouse_id: null, gift_recipient: '', bojun_status: 'pending', pickup_status: 'picked_up', remark: '' }
  barcode.value = ''
  goodsName.value = ''
  goodsId.value = null
  await load()
}

async function updateStatus(row) {
  await outboundApi.update(row.id, { bojun_status: row.bojun_status })
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  await load()
})
</script>
