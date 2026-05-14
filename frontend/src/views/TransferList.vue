<template>
  <div class="transfer-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>调拨记录</span>
          <el-button type="primary" link @click="$router.push('/transfer')">新建调拨</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="待审批" name="pending">
          <el-table :data="pendingList" v-loading="loading" stripe>
            <el-table-column prop="transfer_no" label="调拨单号" width="180" />
            <el-table-column prop="transfer_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ getTypeText(row.transfer_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="from_warehouse_name" label="调出仓库" width="120" />
            <el-table-column prop="to_warehouse_name" label="调入方" width="120" />
            <el-table-column prop="goods_name" label="商品" min-width="150" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="sales_tag" label="销售标签" width="150" />
            <el-table-column prop="created_at" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="success" link size="small" @click="approve(row)">审批</el-button>
                <el-button type="danger" link size="small" @click="reverse(row)">驳回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <el-table :data="completedList" v-loading="loading" stripe>
            <el-table-column prop="transfer_no" label="调拨单号" width="180" />
            <el-table-column prop="transfer_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag type="success">{{ getTypeText(row.transfer_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="goods_name" label="商品" min-width="150" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="sales_tag" label="销售标签" width="150" />
            <el-table-column prop="approved_by" label="审批人" width="100" />
            <el-table-column prop="approved_at" label="审批时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.approved_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="warning" link size="small" @click="reverseRecord(row)">红冲</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { transferApi } from '../api/modules'

const loading = ref(false)
const activeTab = ref('pending')
const transferList = ref([])

const pendingList = computed(() => transferList.value.filter(item => item.status === 'pending'))
const completedList = computed(() => transferList.value.filter(item => item.status === 'completed'))

const getTypeText = (type) => {
  const map = { outbound: '借出', return: '还货', direct: '直接出库' }
  return map[type] || type
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    transferList.value = await transferApi.list()
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

const approve = async (row) => {
  try {
    await ElMessageBox.confirm('确认审批通过此调拨单?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await transferApi.approve(row.id, '仓管员')
    ElMessage.success('审批成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审批失败')
    }
  }
}

const reverse = async (row) => {
  try {
    await ElMessageBox.confirm('确认驳回此调拨单?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await transferApi.reverse(row.id, '不符合调拨条件')
    ElMessage.success('已驳回')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const reverseRecord = async (row) => {
  try {
    await ElMessageBox.confirm('确认红冲此记录? 红冲后库存将恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await transferApi.reverse(row.id, '红冲操作')
    ElMessage.success('红冲成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.transfer-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
