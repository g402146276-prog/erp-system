<template>
  <div class="inbound-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>入库记录</span>
          <el-button type="primary" link @click="$router.push('/inbound')">新增入库</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="boniu_order_no" label="伯俊订单号" width="180" />
        <el-table-column prop="warehouse_name" label="仓库" width="120" />
        <el-table-column prop="goods_name" label="商品" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="created_at" label="入库时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { inboundApi } from '../api/modules'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const skip = (pagination.page - 1) * pagination.pageSize
    const data = await inboundApi.list({ skip, limit: pagination.pageSize })
    tableData.value = data
    pagination.total = data.length
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.inbound-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
