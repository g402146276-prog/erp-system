import api from './index'

export const authApi = {
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  initAdmin: () => api.post('/auth/init-admin')
}

export const locationApi = {
  list: (params) => api.get('/locations/', { params }),
  create: (data) => api.post('/locations/', data),
  delete: (id) => api.delete(`/locations/${id}`),
  setGoodsLocation: (params) => api.post('/goods-location', null, { params }),
  getGoodsLocations: (goodsId) => api.get(`/locations/goods-location/${goodsId}`),
  scan: (barcode) => api.get(`/locations/scan/${barcode}`)
}

export const adjustmentApi = {
  list: (params) => api.get('/adjustments/', { params }),
  get: (id) => api.get(`/adjustments/${id}`),
  create: (data) => api.post('/adjustments/', data),
  apply: (id) => api.put(`/adjustments/${id}/apply`),
  cancel: (id) => api.put(`/adjustments/${id}/cancel`)
}

export const stockApiExt = {
  detail: (goodsId) => api.get(`/stock/detail/${goodsId}`),
  query: (params) => api.get('/stock/query', { params })
}

// 仓库管理人
export const warehouseManagerApi = {
  get: (warehouseId) => api.get(`/warehouse-managers/${warehouseId}`),
  assign: (data) => api.post('/warehouse-managers/', data),
  getUserWarehouses: (userId) => api.get(`/warehouse-managers/user/${userId}/warehouses`),
}

// 审批规则
export const approvalRuleApi = {
  list: () => api.get('/approval-rules/'),
  create: (data) => api.post('/approval-rules/', data),
  update: (id, data) => api.put(`/approval-rules/${id}`, data),
  delete: (id) => api.delete(`/approval-rules/${id}`),
  resolve: (params) => api.post('/approval-rules/resolve', null, { params }),
}

// 采购入库
export const purchaseInboundApi = {
  list: (params) => api.get('/purchase-inbound/', { params }),
  create: (data) => api.post('/purchase-inbound/', data),
  batchCreate: (data) => api.post('/purchase-inbound/batch', data),
  summary: (params) => api.get('/purchase-inbound/summary', { params }),
}

// 在途订单
export const intransitOrderApi = {
  list: (params) => api.get('/intransit-orders/', { params }),
  get: (id) => api.get(`/intransit-orders/${id}`),
  create: (data) => api.post('/intransit-orders/', data),
  complete: (id) => api.put(`/intransit-orders/${id}/complete`),
  cancel: (id) => api.put(`/intransit-orders/${id}/cancel`),
  linkTransfer: (orderId, transferApplyId) => api.post(`/intransit-orders/${orderId}/transfer`, null, { params: { transfer_apply_id: transferApplyId } }),
  linkOutbound: (orderId, outboundId) => api.post(`/intransit-orders/${orderId}/outbound`, null, { params: { outbound_id: outboundId } }),
}

// 调拨申请单
export const transferApplyApi = {
  list: (params) => api.get('/transfer-apply/', { params }),
  get: (id) => api.get(`/transfer-apply/${id}`),
  create: (data) => api.post('/transfer-apply/', data),
  approve: (id, data) => api.put(`/transfer-apply/${id}/approve`, data),
  complete: (id) => api.put(`/transfer-apply/${id}/complete`),
  cancel: (id) => api.put(`/transfer-apply/${id}/cancel`),
}

// 出库单
export const outboundApi = {
  list: (params) => api.get('/outbound/', { params }),
  get: (id) => api.get(`/outbound/${id}`),
  create: (data) => api.post('/outbound/', data),
  update: (id, data) => api.put(`/outbound/${id}`, data),
  reverse: (id) => api.put(`/outbound/${id}/reverse`),
}

// 赠送单
export const giftApi = {
  list: (params) => api.get('/gift/', { params }),
  summary: () => api.get('/gift/summary'),
  reconciliation: (goodsId) => api.get(`/gift/reconciliation`, { params: { goods_id: goodsId } }),
}

// 对账看板
export const reconciliationApi = {
  list: (params) => api.get('/reconciliation/', { params }),
  detail: (goodsId) => api.get(`/reconciliation/detail/${goodsId}`),
}
