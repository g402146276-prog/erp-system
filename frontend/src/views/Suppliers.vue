<template>
  <div class="suppliers-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>供应商档案管理</span>
          <el-button type="primary" size="small" @click="addSupplier">
            <el-icon><plus /></el-icon>
            添加供应商
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="供应商编码/名称" clearable @keyup.enter="loadSuppliers" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadSuppliers">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 供应商列表 -->
      <el-table :data="suppliers" v-loading="loading" style="width: 100%">
        <el-table-column prop="code" label="供应商编码" width="120" />
        <el-table-column prop="name" label="供应商名称" min-width="150" />
        <el-table-column prop="short_name" label="简称" width="100" />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="mobile" label="手机" width="130" />
        <el-table-column prop="email" label="邮箱" width="150" />
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="scope">
            <el-switch :value="scope.row.is_active" @change="toggleStatus(scope.row)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editSupplier(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteSupplier(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加/编辑对话框 -->
      <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑供应商' : '添加供应商'" width="600px">
        <el-form :model="form" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="供应商编码" prop="code" :rules="[{ required: true, message: '请输入供应商编码' }]">
                <el-input v-model="form.code" :disabled="isEdit" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="供应商名称" prop="name" :rules="[{ required: true, message: '请输入供应商名称' }]">
                <el-input v-model="form.name" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="简称">
                <el-input v-model="form.short_name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系人">
                <el-input v-model="form.contact" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="电话">
                <el-input v-model="form.phone" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="手机">
                <el-input v-model="form.mobile" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" />
          </el-form-item>
          <el-form-item label="地址">
            <el-input v-model="form.address" type="textarea" :rows="2" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="银行信息">
                <el-input v-model="form.bank_info" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="税号">
                <el-input v-model="form.tax_no" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveSupplier">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { supplierApi } from '../api/modules'

const loading = ref(false)
const suppliers = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const searchForm = reactive({
  keyword: '',
  is_active: ''
})

const form = reactive({
  code: '',
  name: '',
  short_name: '',
  contact: '',
  phone: '',
  mobile: '',
  email: '',
  address: '',
  bank_info: '',
  tax_no: '',
  remark: ''
})

const loadSuppliers = async () => {
  loading.value = true
  try {
    const params = {
      keyword: searchForm.keyword || undefined,
    }
    if (searchForm.is_active === '' || searchForm.is_active === undefined) {
      params.is_active = undefined
    } else {
      params.is_active = searchForm.is_active
    }
    suppliers.value = await supplierApi.list(params)
  } catch (error) {
    ElMessage.error('加载供应商列表失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.is_active = ''
  loadSuppliers()
}

const addSupplier = () => {
  isEdit.value = false
  editId.value = null
  form.code = ''
  form.name = ''
  form.short_name = ''
  form.contact = ''
  form.phone = ''
  form.mobile = ''
  form.email = ''
  form.address = ''
  form.bank_info = ''
  form.tax_no = ''
  form.remark = ''
  showAddDialog.value = true
}

const editSupplier = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.code = row.code
  form.name = row.name
  form.short_name = row.short_name || ''
  form.contact = row.contact || ''
  form.phone = row.phone || ''
  form.mobile = row.mobile || ''
  form.email = row.email || ''
  form.address = row.address || ''
  form.bank_info = row.bank_info || ''
  form.tax_no = row.tax_no || ''
  form.remark = row.remark || ''
  showAddDialog.value = true
}

const saveSupplier = async () => {
  if (!form.code || !form.name) {
    ElMessage.error('请填写必填字段')
    return
  }

  try {
    if (isEdit.value) {
      await supplierApi.update(editId.value, {
        name: form.name,
        short_name: form.short_name,
        contact: form.contact,
        phone: form.phone,
        mobile: form.mobile,
        email: form.email,
        address: form.address,
        bank_info: form.bank_info,
        tax_no: form.tax_no,
        remark: form.remark
      })
      ElMessage.success('修改成功')
    } else {
      await supplierApi.create({ ...form })
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    loadSuppliers()
  } catch (error) {
    ElMessage.error(isEdit.value ? '修改失败' : '添加失败')
  }
}

const deleteSupplier = async (row) => {
  if (confirm(`确定要删除供应商 "${row.name}" 吗？`)) {
    try {
      await supplierApi.delete(row.id)
      ElMessage.success('删除成功')
      loadSuppliers()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }
}

const toggleStatus = async (row) => {
  const original = row.is_active
  try {
    await supplierApi.update(row.id, { is_active: !original })
    row.is_active = !original
    ElMessage.success('状态已更新')
  } catch (error) {
    row.is_active = original
    ElMessage.error('更新失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

loadSuppliers()
</script>

<style scoped>
.suppliers-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
