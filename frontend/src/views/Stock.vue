<template>
  <div class="stock-container">
    <el-card>
      <template #header>
        <span>库存查询</span>
      </template>

      <el-form :inline="true" :model="queryForm">
        <el-form-item label="商品名称">
          <el-input v-model="queryForm.goods_name" placeholder="输入商品名称" clearable />
        </el-form-item>
        <el-form-item label="条码">
          <el-input v-model="queryForm.barcode" placeholder="输入条码" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="商品名称" min-width="150" />
        <el-table-column prop="barcode" label="条码" width="150" />
        <el-table-column prop="spec" label="规格" width="150" />
        <el-table-column prop="total_quantity" label="总库存" width="100">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.total_quantity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="仓库分布" min-width="300">
          <template #default="{ row }">
            <div v-for="ws in row.warehouse_stocks" :key="ws.warehouse_id" style="margin-bottom: 5px;">
              <el-tag size="small">{{ ws.warehouse_name }}: {{ ws.quantity }}</el-tag>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { stockApi } from '../api/modules'

const loading = ref(false)
const tableData = ref([])
const queryForm = reactive({
  goods_name: '',
  barcode: ''
})

const search = async () => {
  loading.value = true
  try {
    tableData.value = await stockApi.query(queryForm)
  } catch (error) {
    console.error('Failed to search:', error)
  } finally {
    loading.value = false
  }
}

const reset = () => {
  queryForm.goods_name = ''
  queryForm.barcode = ''
  search()
}

onMounted(() => {
  search()
})
</script>

<style scoped>
.stock-container {
  padding: 20px;
}
</style>
