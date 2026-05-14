<template>
  <div class="inbound-list-container">
    <h2 style="margin-bottom:16px">入库记录</h2>

    <!-- ===== 查询面板 ===== -->
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true" size="small" label-width="auto">
        <el-form-item label="日期">
          <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:240px" />
        </el-form-item>
        <el-form-item label="伯俊单号">
          <el-input v-model="filters.bojun_order_no" placeholder="模糊搜索" style="width:140px" clearable />
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="filters.warehouse_id" clearable placeholder="全部" style="width:130px">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="商品">
          <el-input v-model="filters.keyword" placeholder="条码/品名" style="width:140px" clearable />
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="filters.operator" placeholder="模糊搜索" style="width:120px" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- ===== 数据表格 ===== -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe border size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="boniu_order_no" label="伯俊单号" width="150" />
        <el-table-column label="仓库" width="110">
          <template #default="{row}">{{ row.warehouse_name || row.warehouse_id }}</template>
        </el-table-column>
        <el-table-column label="商品" min-width="150">
          <template #default="{row}">{{ row.goods_name || `ID:${row.goods_id}` }}</template>
        </el-table-column>
        <el-table-column prop="goods_barcode" label="条码" width="130" />
        <el-table-column prop="quantity" label="数量" width="65" header-align="center" align="center" />
        <el-table-column prop="operator" label="操作人" width="90" />
        <el-table-column prop="created_at" label="入库时间" width="165">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" />
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top:16px;justify-content:center"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { inboundApi, warehouseApi } from '../api/modules'

const loading = ref(false)
const tableData = ref([])
const warehouses = ref([])

const filters = reactive({
  dateRange: null,
  bojun_order_no: '',
  warehouse_id: null,
  keyword: '',
  operator: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

function buildParams() {
  const params = {
    skip: (pagination.page - 1) * pagination.pageSize,
    limit: pagination.pageSize,
  }
  if (filters.dateRange && filters.dateRange.length === 2) {
    params.date_from = filters.dateRange[0]
    params.date_to = filters.dateRange[1]
  }
  if (filters.bojun_order_no) params.bojun_order_no = filters.bojun_order_no
  if (filters.warehouse_id) params.warehouse_id = filters.warehouse_id
  if (filters.keyword) params.keyword = filters.keyword
  if (filters.operator) params.operator = filters.operator
  return params
}

async function loadData() {
  loading.value = true
  try {
    const data = await inboundApi.list(buildParams())
    tableData.value = data
    pagination.total = data.length < pagination.pageSize
      ? (pagination.page - 1) * pagination.pageSize + data.length
      : pagination.page * pagination.pageSize + 1
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

function search() {
  pagination.page = 1
  loadData()
}

function resetFilters() {
  filters.dateRange = null
  filters.bojun_order_no = ''
  filters.warehouse_id = null
  filters.keyword = ''
  filters.operator = ''
  pagination.page = 1
  loadData()
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  loadData()
})
</script>

<style scoped>
.inbound-list-container {
  padding: 0;
}
</style>
