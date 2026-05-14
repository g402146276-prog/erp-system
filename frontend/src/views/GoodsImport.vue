<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>商品档案</h2>
      <div>
        <el-button @click="showImport=true">CSV导入</el-button>
        <el-button type="primary" @click="openAdd">添加商品</el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-form :inline="true" style="margin-bottom:12px">
      <el-form-item>
        <el-input v-model="keyword" placeholder="搜索名称/条码" clearable style="width:260px" @keyup.enter="load" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="load">搜索</el-button>
        <el-button @click="keyword='';load()">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 商品列表 -->
    <el-table :data="list" border stripe v-loading="loading" max-height="calc(100vh - 320px)">
      <el-table-column prop="barcode" label="条码" width="150" />
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column prop="spec" label="规格" width="160" />
      <el-table-column prop="unit" label="单位" width="60" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="price" label="单价" width="80" />
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="editId?'编辑商品':'添加商品'" width="500px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="条码" prop="barcode"><el-input v-model="form.barcode" :disabled="!!editId" /></el-form-item>
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="规格"><el-input v-model="form.spec" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" allow-create filterable clearable style="width:100%">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="单价"><el-input-number v-model="form.price" :precision="2" :min="0" style="width:200px" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- CSV导入对话框 -->
    <el-dialog v-model="showImport" title="CSV导入商品" width="500px">
      <el-alert title="必填列：条码、名称。可选列：规格、单位、分类、单价、备注。" type="info" :closable="false" show-icon style="margin-bottom:12px" />
      <el-upload
        drag
        action="/api/goods-import/upload"
        :headers="uploadHeaders"
        accept=".csv"
        :on-success="importSuccess"
        :on-error="importError"
        :before-upload="beforeUpload"
        :data="{ encoding: 'auto' }"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
        <template #tip><div class="el-upload__tip">只能上传 CSV 文件</div></template>
      </el-upload>
      <template #footer>
        <el-button @click="downloadTemplate">下载模板</el-button>
        <el-button @click="showImport=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { goodsApi, goodsImportApi } from '../api/modules'

const list = ref([])
const loading = ref(false)
const keyword = ref('')
const showDialog = ref(false)
const showImport = ref(false)
const editId = ref(null)
const formRef = ref(null)
const form = ref({ barcode: '', name: '', spec: '', unit: '个', category: '', price: 0, remark: '' })
const formRules = {
  barcode: [{ required: true, message: '请输入条码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}
const categories = ref([])
const uploadHeaders = ref({ Authorization: 'Bearer ' + (localStorage.getItem('erp_token') || '') })

async function load() {
  loading.value = true
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    list.value = await goodsApi.list(params)
    // 收集分类
    const cats = new Set()
    list.value.forEach(g => g.category && cats.add(g.category))
    categories.value = [...cats].sort()
  } catch (e) {
    ElMessage.error('加载失败')
  }
  loading.value = false
}

function openAdd() {
  editId.value = null
  form.value = { barcode: '', name: '', spec: '', unit: '个', category: '', price: 0, remark: '' }
  showDialog.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.value = { barcode: row.barcode, name: row.name, spec: row.spec || '', unit: row.unit || '个', category: row.category || '', price: row.price || 0, remark: row.remark || '' }
  showDialog.value = true
}

async function save() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (editId.value) {
      await goodsApi.update(editId.value, form.value)
      ElMessage.success('已更新')
    } else {
      await goodsApi.create(form.value)
      ElMessage.success('已添加')
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
    await goodsApi.delete(row.id)
    ElMessage.success('已删除')
    await load()
  } catch {}
}

function beforeUpload(file) {
  if (!file.name.endsWith('.csv')) { ElMessage.error('只能上传 CSV'); return false }
  return true
}

function importSuccess() {
  ElMessage.success('导入成功')
  showImport.value = false
  load()
}

function importError(err) {
  const detail = err?.response?.data?.detail || err?.message || '未知错误'
  ElMessage.error('导入失败: ' + detail)
}

function downloadTemplate() {
  const tpl = '条码,名称,规格,单位,分类,单价,备注\nC010114090155,和合璧鸳鸯炉,约79*10mm/0.25kg,个,香炉,299,精品\n'
  const blob = new Blob([tpl], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '商品导入模板.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}

onMounted(load)
</script>
