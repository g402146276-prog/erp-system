<template>
  <div>
    <h2>对账看板</h2>
    <el-alert title="对账公式：伯俊库存 ≈ 实物库存 + 赠送待核销 + 借出未还 - 出库未取(伯俊已出库)" type="success" :closable="false" show-icon style="margin-bottom:16px" />
    <el-form :inline="true" style="margin-bottom:16px">
      <el-form-item label="商品条码"><el-input v-model="barcode" placeholder="扫码或输入" @keyup.enter="search" /></el-form-item>
      <el-form-item><el-button type="primary" @click="search">查询</el-button></el-form-item>
    </el-form>
    <el-table :data="list" border stripe @row-click="showDetail">
      <el-table-column prop="goods_barcode" label="条码" width="140" />
      <el-table-column prop="goods_name" label="商品名称" min-width="180" />
      <el-table-column prop="spec" label="规格" width="100" />
      <el-table-column prop="physical_stock" label="实物库存" width="100" header-align="center" align="center" />
      <el-table-column prop="gift_pending" label="+赠送待核销" width="120" header-align="center" align="center">
        <template #default="{row}"><span style="color:#e6a23c">{{ row.gift_pending }}</span></template>
      </el-table-column>
      <el-table-column prop="borrowed_out" label="+借出未还" width="110" header-align="center" align="center">
        <template #default="{row}"><span style="color:#409eff">{{ row.borrowed_out }}</span></template>
      </el-table-column>
      <el-table-column prop="stored_bojun_out" label="-出库未取(伯俊已出)" width="160" header-align="center" align="center">
        <template #default="{row}"><span style="color:#f56c6c">{{ row.stored_bojun_out }}</span></template>
      </el-table-column>
      <el-table-column prop="suggested_bojun" label="≈应存(伯俊参考)" width="150" header-align="center" align="center" sortable>
        <template #default="{row}"><strong>{{ row.suggested_bojun }}</strong></template>
      </el-table-column>
    </el-table>
    <p v-if="!list.length" style="color:#999;text-align:center;padding:40px">请输入商品条码查询</p>

    <el-dialog v-model="detailVisible" title="对账明细" width="700px">
      <template v-if="detail">
        <h4>{{ detail.goods.name }} ({{ detail.goods.barcode }})</h4>
        <el-descriptions :column="2" border style="margin:12px 0">
          <el-descriptions-item label="各仓库存">
            <div v-for="s in detail.stocks" :key="s.warehouse_id">{{ s.warehouse_name || '仓库#'+s.warehouse_id }}: {{ s.quantity }}</div>
          </el-descriptions-item>
        </el-descriptions>
        <el-tabs>
          <el-tab-pane label="赠送单">
            <el-table :data="detail.gift_orders" v-if="detail.gift_orders.length" size="small">
              <el-table-column prop="outbound_no" label="单号" width="160" />
              <el-table-column prop="quantity" label="数量" width="80" />
              <el-table-column label="伯俊状态">
                <template #default="{row}">{{ {outbound:'已出库',unknown:'未知',pending:'待核销'}[row.bojun_status] }}</template>
              </el-table-column>
              <el-table-column prop="created_at" label="时间" width="160" />
            </el-table>
            <p v-else style="color:#999">无赠送记录</p>
          </el-tab-pane>
          <el-tab-pane label="借出记录">
            <el-table :data="detail.borrow_orders" v-if="detail.borrow_orders.length" size="small">
              <el-table-column prop="apply_no" label="单号" width="160" />
              <el-table-column prop="quantity" label="数量" width="80" />
              <el-table-column prop="status" label="状态" width="80" />
              <el-table-column prop="created_at" label="时间" width="160" />
            </el-table>
            <p v-else style="color:#999">无借出记录</p>
          </el-tab-pane>
          <el-tab-pane label="出库未取(暂存)">
            <el-table :data="detail.stored_orders" v-if="detail.stored_orders.length" size="small">
              <el-table-column prop="outbound_no" label="单号" width="160" />
              <el-table-column prop="quantity" label="数量" width="80" />
              <el-table-column label="伯俊状态">
                <template #default="{row}">{{ {outbound:'已出库',unknown:'未知',pending:'待核销'}[row.bojun_status] || row.bojun_status }}</template>
              </el-table-column>
              <el-table-column prop="created_at" label="时间" width="160" />
            </el-table>
            <p v-else style="color:#999">无暂存记录</p>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { reconciliationApi } from '../api/modules_ext'

const list = ref([])
const barcode = ref('')
const detailVisible = ref(false)
const detail = ref(null)

async function search() {
  if (!barcode.value) return
  list.value = await reconciliationApi.list({ barcode: barcode.value })
}

async function showDetail(row) {
  detail.value = await reconciliationApi.detail(row.goods_id)
  detailVisible.value = true
}
</script>
