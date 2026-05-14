<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>调拨申请单</h2>
      <el-button type="primary" @click="showCreate=true">新建调拨申请</el-button>
    </div>
    <el-alert title="移库=仓库间移动库存；借样=销售借出（需要归还）；报损=货物损坏→报损仓。" type="info" :closable="false" show-icon style="margin:12px 0" />
    <el-tabs v-model="tab">
      <el-tab-pane label="待审批" name="pending" />
      <el-tab-pane label="已审批" name="approved" />
      <el-tab-pane label="全部" name="all" />
    </el-tabs>
    <el-table :data="list" border stripe>
      <el-table-column prop="apply_no" label="单号" width="150" />
      <el-table-column label="类型" width="80">
        <template #default="{row}">{{ {move:'移库',borrow:'借样',damage:'报损'}[row.transfer_type] }}</template>
      </el-table-column>
      <el-table-column label="调出→调入" min-width="200">
        <template #default="{row}">{{ row.source_warehouse_name }} → {{ row.dest_warehouse_name }}</template>
      </el-table-column>
      <el-table-column prop="goods_barcode" label="条码" width="120" />
      <el-table-column prop="goods_name" label="商品" min-width="150" />
      <el-table-column prop="quantity" label="数量" width="70" />
      <el-table-column prop="applicant" label="申请人" width="80" />
      <el-table-column label="状态" width="90">
        <template #default="{row}">
          <el-tag :type="{draft:'info',pending:'warning',approved:'success',rejected:'danger',completed:'',cancelled:'info'}[row.status]">
            {{ {draft:'草稿',pending:'待审批',approved:'已审批',rejected:'已拒绝',completed:'已完成',cancelled:'已作废'}[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="原因" min-width="120" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="150" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button v-if="row.status==='pending'" size="small" type="success" @click="approve(row, true)">通过</el-button>
          <el-button v-if="row.status==='pending'" size="small" type="danger" @click="reject(row)">拒绝</el-button>
          <el-button v-if="row.status==='approved' && row.transfer_type==='borrow'" size="small" @click="completeBorrow(row)">归还</el-button>
          <el-button v-if="row.status==='draft'||row.status==='pending'" size="small" @click="cancelApply(row)">作废</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreate" title="新建调拨申请" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="调拨类型">
          <el-radio-group v-model="form.transfer_type">
            <el-radio value="move">移库</el-radio>
            <el-radio value="borrow">借样</el-radio>
            <el-radio value="damage">报损</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="商品条码">
          <el-input v-model="barcode" placeholder="扫码输入" @change="loadGoods" style="width:200px" />
          <span style="margin-left:8px;color:#999">{{ goodsName }}</span>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
        <el-form-item label="调出仓库">
          <el-select v-model="form.source_warehouse_id" filterable>
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调入仓库">
          <el-select v-model="form.dest_warehouse_id" filterable>
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因说明（报损必填）">
          <el-input v-model="form.reason" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate=false">取消</el-button>
        <el-button type="primary" @click="createApply">提交申请</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReject" title="拒绝原因" width="400px">
      <el-input v-model="rejectReason" type="textarea" placeholder="请输入拒绝原因" />
      <template #footer>
        <el-button @click="showReject=false">取消</el-button>
        <el-button type="danger" @click="doReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { transferApplyApi } from '../api/modules_ext'
import { goodsApi, warehouseApi } from '../api/modules'

const list = ref([])
const tab = ref('pending')
const showCreate = ref(false)
const showReject = ref(false)
const rejectTarget = ref(null)
const rejectReason = ref('')
const barcode = ref('')
const goodsName = ref('')
const goodsId = ref(null)
const warehouses = ref([])
const form = ref({
  transfer_type: 'move', quantity: 1,
  source_warehouse_id: null, dest_warehouse_id: null, reason: '',
})

async function load() {
  const params = {}
  if (tab.value !== 'all') params.status = tab.value
  list.value = await transferApplyApi.list(params)
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

async function createApply() {
  if (!goodsId.value || !form.value.source_warehouse_id || !form.value.dest_warehouse_id) return
  await transferApplyApi.create({
    transfer_type: form.value.transfer_type,
    source_warehouse_id: form.value.source_warehouse_id,
    dest_warehouse_id: form.value.dest_warehouse_id,
    goods_id: goodsId.value,
    quantity: form.value.quantity,
    reason: form.value.reason,
  })
  showCreate.value = false
  form.value = { transfer_type: 'move', quantity: 1, source_warehouse_id: null, dest_warehouse_id: null, reason: '' }
  barcode.value = ''
  goodsName.value = ''
  goodsId.value = null
  await load()
}

async function approve(row, approved) {
  await transferApplyApi.approve(row.id, { approve: true })
  await load()
}

function reject(row) {
  rejectTarget.value = row
  rejectReason.value = ''
  showReject.value = true
}

async function doReject() {
  await transferApplyApi.approve(rejectTarget.value.id, { approve: false, reject_reason: rejectReason.value })
  showReject.value = false
  await load()
}

async function completeBorrow(row) {
  await transferApplyApi.complete(row.id)
  await load()
}

async function cancelApply(row) {
  await transferApplyApi.cancel(row.id)
  await load()
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  await load()
})
</script>
