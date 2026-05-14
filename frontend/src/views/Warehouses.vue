<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>仓库管理</h2>
      <el-button type="primary" @click="openAdd">新建仓库</el-button>
    </div>

    <el-table :data="list" border stripe v-loading="loading">
      <el-table-column prop="code" label="编码" width="100" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column label="类型" width="120">
        <template #default="{row}">
          <el-tag :type="{entity:'primary',virtual_sales:'success',virtual_exhibit:'warning',virtual_damage:'danger'}[row.warehouse_type]" size="small">
            {{ {entity:'实体仓',virtual_sales:'销售虚拟仓',virtual_exhibit:'展台虚拟仓',virtual_damage:'报损仓'}[row.warehouse_type] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{row}">
          <el-tag :type="row.is_active?'success':'info'" size="small">{{ row.is_active?'启用':'停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" :title="editId?'编辑仓库':'新建仓库'" width="500px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="仓库编码" prop="code"><el-input v-model="form.code" :disabled="!!editId" /></el-form-item>
        <el-form-item label="仓库名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="仓库类型">
          <el-select v-model="form.warehouse_type" style="width:100%">
            <el-option label="实体仓" value="entity" />
            <el-option label="销售虚拟仓" value="virtual_sales" />
            <el-option label="展台虚拟仓" value="virtual_exhibit" />
            <el-option label="报损仓" value="virtual_damage" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { warehouseApi } from '../api/modules'

const list = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editId = ref(null)
const formRef = ref(null)
const formRules = {
  code: [{ required: true, message: '请输入仓库编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }]
}
const form = ref({ code: '', name: '', warehouse_type: 'entity', is_active: true, remark: '' })

async function load() {
  loading.value = true
  try {
    list.value = await warehouseApi.list()
  } catch { ElMessage.error('加载失败') }
  loading.value = false
}

function openAdd() {
  editId.value = null
  form.value = { code: '', name: '', warehouse_type: 'entity', is_active: true, remark: '' }
  // 自动生成编码 WH001, WH002 ...
  let maxNum = 0
  list.value.forEach(w => {
    const m = (w.code || '').match(/WH(\d+)$/i)
    if (m) maxNum = Math.max(maxNum, parseInt(m[1]))
  })
  form.value.code = 'WH' + String(maxNum + 1).padStart(3, '0')
  showDialog.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.value = { code: row.code, name: row.name, warehouse_type: row.warehouse_type, is_active: row.is_active, remark: row.remark || '' }
  showDialog.value = true
}

async function save() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (editId.value) {
      await warehouseApi.update(editId.value, form.value)
      ElMessage.success('已更新')
    } else {
      await warehouseApi.create(form.value)
      ElMessage.success('已创建')
    }
    showDialog.value = false
    await load()
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.message || '保存失败'
    ElMessage.error(detail)
  }
}

async function del(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.name}」？`, '确认')
    await warehouseApi.delete(row.id)
    ElMessage.success('已删除')
    await load()
  } catch (e) {
    if (e !== 'cancel') {
      const detail = e?.response?.data?.detail || e?.message || '删除失败'
      ElMessage.error(detail)
    }
  }
}

onMounted(load)
</script>
