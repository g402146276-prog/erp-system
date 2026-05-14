import api from './index'

export const goodsApi = {
  list: (params) => api.get('/goods/', { params }),
  get: (id) => api.get(`/goods/${id}`),
  getByBarcode: (barcode) => api.get(`/goods/barcode/${barcode}`),
  create: (data) => api.post('/goods/', data),
  update: (id, data) => api.put(`/goods/${id}`, data),
  delete: (id) => api.delete(`/goods/${id}`)
}

export const warehouseApi = {
  list: (params) => api.get('/warehouses/', { params }),
  get: (id) => api.get(`/warehouses/${id}`),
  create: (data) => api.post('/warehouses/', data),
  update: (id, data) => api.put(`/warehouses/${id}`, data),
  delete: (id) => api.delete(`/warehouses/${id}`)
}

export const inboundApi = {
  list: (params) => api.get('/inbound/', { params }),
  get: (id) => api.get(`/inbound/${id}`),
  create: (data) => api.post('/inbound/', data),
  delete: (id) => api.delete(`/inbound/${id}`)
}

export const inboundApplyApi = {
  list: (params) => api.get('/inbound-apply/', { params }),
  get: (id) => api.get(`/inbound-apply/${id}`),
  create: (data) => api.post('/inbound-apply/', data),
  update: (id, data) => api.put(`/inbound-apply/${id}`, data),
  delete: (id) => api.delete(`/inbound-apply/${id}`)
}

export const transferApi = {
  list: (params) => api.get('/transfer/', { params }),
  get: (id) => api.get(`/transfer/${id}`),
  create: (data) => api.post('/transfer/', data),
  approve: (id, approvedBy) => api.put(`/transfer/${id}/approve`, { approved_by: approvedBy }),
  reverse: (id, remark) => api.put(`/transfer/${id}/reverse`, { reversed_remark: remark }),
  delete: (id) => api.delete(`/transfer/${id}`)
}

export const stockApi = {
  list: (params) => api.get('/stock/', { params }),
  query: (params) => api.get('/stock/query', { params }),
  get: (id) => api.get(`/stock/${id}`)
}

export const goodsImportApi = {
  list: (params) => api.get('/goods-import/', { params }),
  get: (id) => api.get(`/goods-import/${id}`),
  template: () => api.get('/goods-import/template/download')
}

export const personApi = {
  list: (params) => api.get('/persons/', { params }),
  get: (id) => api.get(`/persons/${id}`),
  create: (data) => api.post('/persons/', data),
  update: (id, data) => api.put(`/persons/${id}`, data),
  delete: (id) => api.delete(`/persons/${id}`)
}

export const supplierApi = {
  list: (params) => api.get('/suppliers/', { params }),
  get: (id) => api.get(`/suppliers/${id}`),
  create: (data) => api.post('/suppliers/', data),
  update: (id, data) => api.put(`/suppliers/${id}`, data),
  delete: (id) => api.delete(`/suppliers/${id}`)
}
