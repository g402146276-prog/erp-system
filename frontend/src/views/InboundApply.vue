<template>
  <div class="inbound-apply-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>入库申请单</span>
          <el-button type="primary" @click="showAddDialog = true">新建申请</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="待入库" name="pending">
          <el-table :data="pendingList" v-loading="loading" stripe>
            <el-table-column prop="apply_no" label="申请单号" width="180" />
            <el-table-column prop="apply_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.apply_type === 'direct' ? 'primary' : 'success'">
                  {{ row.apply_type === 'direct' ? '直发客户' : '调拨订单' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column prop="boniu_order_no" label="伯俊订单号" width="180" />
            <el-table-column prop="total_quantity" label="数量" width="80" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewDetail(row)">查看</el-button>
                <el-button type="success" link size="small" @click="markArrived(row)">标记到货</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <el-table :data="completedList" v-loading="loading" stripe>
            <el-table-column prop="apply_no" label="申请单号" width="180" />
            <el-table-column prop="apply_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.apply_type === 'direct' ? 'primary' : 'success'">
                  {{ row.apply_type === 'direct' ? '直发客户' : '调拨订单' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column prop="total_quantity" label="数量" width="80" />
            <el-table-column prop="created_at" label="完成时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.updated_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新建入库申请" width="600px">
      <el-form :model="applyForm" ref="applyFormRef" label-width="120px">
        <el-form-item label="申请类型" prop="apply_type">
          <el-radio-group v-model="applyForm.apply_type">
            <el-radio label="direct">直发客户</el-radio>
            <el-radio label="transfer">调拨订单</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="客户/调拨方" prop="customer_name">
          <el-input v-model="applyForm.customer_name" placeholder="请输入客户姓名或调拨方" />
        </el-form-item>
        <el-form-item label="伯俊订单号">
          <el-input v-model="applyForm.boniu_order_no" placeholder="直发客户订单必填" />
        </el-form-item>
        <el-form-item label="商品明细" prop="goods_details">
          <el-input v-model="applyForm.goods_details" type="textarea" rows="3" placeholder="格式: [{&quot;barcode&quot;:&quot;xxx&quot;,&quot;name&quot;:&quot;商品&quot;,&quot;quantity&quot;:10}]" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="applyForm.remark" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitApply" :loading="loading">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { inboundApplyApi } from '../api/modules'

const loading = ref(false)
const activeTab = ref('pending')
const showAddDialog = ref(false)
const applyList = ref([])
const applyFormRef = ref(null)

const applyForm = reactive({
  apply_type: 'direct',
  applicant_id: 1,
  customer_name: '',
  boniu_order_no: '',
  goods_details: '',
  remark: ''
})

const pendingList = computed(() => applyList.value.filter(item => item.status !== 'completed'))
const completedList = computed(() => applyList.value.filter(item => item.status === 'completed'))

const getStatusType = (status) => {
  const map = { pending: 'warning', part: 'info', completed: 'success', cancelled: 'danger' }
  return map[status] || ''
}

const getStatusText = (status) => {
  const map = { pending: '待入库', part: '部分到货', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    applyList.value = await inboundApplyApi.list()
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

const submitApply = async () => {
  loading.value = true
  try {
    await inboundApplyApi.create(applyForm)
    ElMessage.success('申请提交成功')
    showAddDialog.value = false
    loadData()
    Object.keys(applyForm).forEach(key => {
      if (key !== 'apply_type' && key !== 'applicant_id') {
        applyForm[key] = ''
      }
    })
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info(`查看申请单: ${row.apply_no}`)
}

const markArrived = (row) => {
  ElMessage.success(`已标记 ${row.apply_no} 到货`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.inbound-apply-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
