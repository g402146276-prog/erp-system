<template>
  <div class="loc-container">
    <div class="loc-header">
      <h2>货位管理</h2>
      <el-button type="primary" size="small" @click="openAdd">+ 新增货位</el-button>
    </div>

    <el-form :inline="true" :model="filterForm">
      <el-form-item label="仓库">
        <el-select v-model="filterForm.warehouse_id" placeholder="选择仓库" clearable @change="load">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
      </el-form-item>
    </el-form>

    <div v-for="loc in locations" :key="loc.id" class="loc-card">
      <div class="loc-top">
        <span class="loc-code">{{ loc.code }}</span>
        <span class="loc-wh">{{ loc.warehouse_name }}</span>
        <el-button text type="danger" size="small" @click="delLoc(loc.id)">删除</el-button>
      </div>
      <div v-if="loc.name" class="loc-name">{{ loc.name }}</div>
    </div>

    <el-empty v-if="!loading && locations.length === 0" description="暂无货位" />

    <el-dialog v-model="showAdd" title="新增货位" width="90%" max-width="500px">
      <el-form :model="addForm" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="所属仓库" prop="warehouse_id">
          <el-select v-model="addForm.warehouse_id" style="width: 100%" @change="autoFillCode">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="货位编码" prop="code">
          <el-input v-model="addForm.code" placeholder="选择仓库后自动生成" />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="addForm.name" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="addLocation">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { warehouseApi } from '../api/modules'
import { locationApi } from '../api/modules_ext'

const showAdd = ref(false)
const saving = ref(false)
const loading = ref(false)
const locations = ref([])
const warehouses = ref([])

const filterForm = ref({ warehouse_id: '' })
const addForm = ref({ warehouse_id: '', code: '', name: '' })
const formRef = ref(null)
const formRules = {
  warehouse_id: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  code: [{ required: true, message: '请输入货位编码', trigger: 'blur' }]
}

async function autoFillCode() {
  const wid = addForm.value.warehouse_id
  if (!wid) return
  try {
    const list = await locationApi.list({ warehouse_id: wid })
    // 提取数字编号，取最大值+1
    let maxNum = 0
    list.forEach(l => {
      const m = (l.code || '').match(/(\d+)$/)
      if (m) maxNum = Math.max(maxNum, parseInt(m[1]))
    })
    addForm.value.code = String(maxNum + 1).padStart(3, '0')
  } catch {
    addForm.value.code = '001'
  }
}

function openAdd() {
  addForm.value = { warehouse_id: '', code: '', name: '' }
  // 默认选中第一个仓库
  if (warehouses.value.length > 0) {
    addForm.value.warehouse_id = warehouses.value[0].id
    autoFillCode()
  }
  showAdd.value = true
}

const load = async () => {
  loading.value = true
  try {
    locations.value = await locationApi.list({ warehouse_id: filterForm.value.warehouse_id || undefined })
  } catch (_) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const addLocation = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await locationApi.create(addForm.value)
    ElMessage.success('新增成功')
    showAdd.value = false
    addForm.value = { warehouse_id: '', code: '', name: '' }
    load()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '新增失败')
  } finally {
    saving.value = false
  }
}

const delLoc = async (id) => {
  try {
    await locationApi.delete(id)
    ElMessage.success('已删除')
    load()
  } catch (_) {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  warehouses.value = await warehouseApi.list()
  load()
})
</script>

<style scoped>
.loc-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
}
.loc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.loc-header h2 { margin: 0; }
.loc-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.loc-top { display: flex; align-items: center; gap: 8px; }
.loc-code { font-weight: bold; font-size: 16px; }
.loc-wh { color: #909399; font-size: 13px; flex: 1; }
.loc-name { margin-top: 4px; color: #606266; font-size: 13px; }
</style>
