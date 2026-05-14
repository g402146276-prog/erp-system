<template>
  <div>
    <h2>审批规则配置</h2>
    <el-alert title="按优先级匹配规则，空条件表示「任意」。新增规则后，调拨申请会自动匹配审批人。" type="info" :closable="false" show-icon style="margin-bottom:16px" />
    <el-button type="primary" @click="showDialog=true" style="margin-bottom:16px">新增规则</el-button>
    <el-table :data="rules" border stripe>
      <el-table-column prop="priority" label="优先级" width="80" />
      <el-table-column label="规则名称" prop="name" />
      <el-table-column label="条件-调出仓库">
        <template #default="{row}">{{ srcWhName(row.source_warehouse_id) || '任意' }}</template>
      </el-table-column>
      <el-table-column label="条件-调入仓库">
        <template #default="{row}">{{ dstWhName(row.dest_warehouse_id) || '任意' }}</template>
      </el-table-column>
      <el-table-column label="条件-调拨类型">
        <template #default="{row}">{{ typeLabel(row.transfer_type) || '任意' }}</template>
      </el-table-column>
      <el-table-column label="审批人">
        <template #default="{row}">{{ userName(row.approver_id) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{row}">
          <el-tag :type="row.is_active?'success':'info'">{{ row.is_active?'启用':'禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <el-button size="small" @click="editRule(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="delRule(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" :title="editId?'编辑规则':'新增规则'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="规则名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="优先级"><el-input-number v-model="form.priority" :min="0" /></el-form-item>
        <el-form-item label="调出仓库">
          <el-select v-model="form.source_warehouse_id" clearable placeholder="任意">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调入仓库">
          <el-select v-model="form.dest_warehouse_id" clearable placeholder="任意">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调拨类型">
          <el-select v-model="form.transfer_type" clearable placeholder="任意">
            <el-option label="移库" value="move" />
            <el-option label="借样" value="borrow" />
            <el-option label="报损" value="damage" />
          </el-select>
        </el-form-item>
        <el-form-item label="审批人">
          <el-select v-model="form.approver_id" filterable>
            <el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog=false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { approvalRuleApi } from '../api/modules_ext'
import { warehouseApi } from '../api/modules'
import { authApi } from '../api/modules_ext'

const rules = ref([])
const warehouses = ref([])
const users = ref([])
const showDialog = ref(false)
const editId = ref(null)
const form = ref({ name: '', priority: 0, source_warehouse_id: null, dest_warehouse_id: null, transfer_type: null, approver_id: null, remark: '' })

function typeLabel(v) { return { move: '移库', borrow: '借样', damage: '报损' }[v] }

function srcWhName(id) { return warehouses.value.find(w => w.id === id)?.name }
function dstWhName(id) { return warehouses.value.find(w => w.id === id)?.name }
function userName(id) { return users.value.find(u => u.id === id)?.display_name }

async function load() {
  rules.value = await approvalRuleApi.list()
  warehouses.value = await warehouseApi.list()
  const me = await authApi.me()
  users.value = [me]
}

function editRule(row) {
  editId.value = row.id
  form.value = { name: row.name, priority: row.priority, source_warehouse_id: row.source_warehouse_id, dest_warehouse_id: row.dest_warehouse_id, transfer_type: row.transfer_type, approver_id: row.approver_id, remark: row.remark || '' }
  showDialog.value = true
}

async function saveRule() {
  if (editId.value) {
    await approvalRuleApi.update(editId.value, form.value)
  } else {
    await approvalRuleApi.create(form.value)
  }
  showDialog.value = false
  editId.value = null
  form.value = { name: '', priority: 0, source_warehouse_id: null, dest_warehouse_id: null, transfer_type: null, approver_id: null, remark: '' }
  await load()
}

async function delRule(row) {
  await approvalRuleApi.delete(row.id)
  await load()
}

onMounted(load)
</script>
