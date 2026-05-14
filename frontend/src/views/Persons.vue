<template>
  <div class="persons-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>人员档案管理</span>
          <el-button type="primary" size="small" @click="addPerson">
            <el-icon><plus /></el-icon>
            添加人员
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="人员编码/姓名" clearable @keyup.enter="loadPersons" />
        </el-form-item>
        <el-form-item label="人员类型">
          <el-select v-model="searchForm.person_type" placeholder="全部" clearable>
            <el-option label="销售" value="sales" />
            <el-option label="仓管" value="warehouse" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPersons">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 人员列表 -->
      <el-table :data="persons" v-loading="loading" style="width: 100%">
        <el-table-column prop="code" label="人员编码" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="person_type" label="类型" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getTypeTagType(scope.row.person_type)">
              {{ getTypeText(scope.row.person_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="phone" label="联系电话" width="130" />
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
            <el-button type="primary" size="small" @click="editPerson(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deletePerson(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加/编辑对话框 -->
      <el-dialog v-model="showAddDialog" :title="isEdit ? '编辑人员' : '添加人员'" width="500px">
        <el-form :model="form" label-width="100px">
          <el-form-item label="人员编码" prop="code" :rules="[{ required: true, message: '请输入人员编码' }]">
            <el-input v-model="form.code" :disabled="isEdit" />
          </el-form-item>
          <el-form-item label="姓名" prop="name" :rules="[{ required: true, message: '请输入姓名' }]">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="人员类型">
            <el-select v-model="form.person_type">
              <el-option label="销售" value="sales" />
              <el-option label="仓管" value="warehouse" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="部门">
            <el-input v-model="form.department" />
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="form.phone" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="savePerson">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { personApi } from '../api/modules'

const loading = ref(false)
const persons = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const searchForm = reactive({
  keyword: '',
  person_type: '',
  is_active: ''
})

const form = reactive({
  code: '',
  name: '',
  person_type: 'sales',
  department: '',
  phone: '',
  remark: ''
})

const loadPersons = async () => {
  loading.value = true
  try {
    const params = {
      keyword: searchForm.keyword || undefined,
      person_type: searchForm.person_type || undefined,
    }
    if (searchForm.is_active === '' || searchForm.is_active === undefined) {
      params.is_active = undefined
    } else {
      params.is_active = searchForm.is_active
    }
    persons.value = await personApi.list(params)
  } catch (error) {
    ElMessage.error('加载人员列表失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.person_type = ''
  searchForm.is_active = ''
  loadPersons()
}

const addPerson = () => {
  isEdit.value = false
  editId.value = null
  form.code = ''
  form.name = ''
  form.person_type = 'sales'
  form.department = ''
  form.phone = ''
  form.remark = ''
  showAddDialog.value = true
}

const editPerson = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.code = row.code
  form.name = row.name
  form.person_type = row.person_type
  form.department = row.department || ''
  form.phone = row.phone || ''
  form.remark = row.remark || ''
  showAddDialog.value = true
}

const savePerson = async () => {
  if (!form.code || !form.name) {
    ElMessage.error('请填写必填字段')
    return
  }

  try {
    if (isEdit.value) {
      await personApi.update(editId.value, {
        name: form.name,
        person_type: form.person_type,
        department: form.department,
        phone: form.phone,
        remark: form.remark
      })
      ElMessage.success('修改成功')
    } else {
      await personApi.create({ ...form })
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    loadPersons()
  } catch (error) {
    ElMessage.error(isEdit.value ? '修改失败' : '添加失败')
  }
}

const deletePerson = async (row) => {
  if (confirm(`确定要删除人员 "${row.name}" 吗？`)) {
    try {
      await personApi.delete(row.id)
      ElMessage.success('删除成功')
      loadPersons()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }
}

const toggleStatus = async (row) => {
  const original = row.is_active
  try {
    await personApi.update(row.id, { is_active: !original })
    row.is_active = !original
    ElMessage.success('状态已更新')
  } catch (error) {
    row.is_active = original
    ElMessage.error('更新失败')
  }
}

const getTypeTagType = (type) => {
  const types = { sales: 'primary', warehouse: 'success', other: 'info' }
  return types[type] || 'info'
}

const getTypeText = (type) => {
  const texts = { sales: '销售', warehouse: '仓管', other: '其他' }
  return texts[type] || type
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

loadPersons()
</script>

<style scoped>
.persons-container {
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
