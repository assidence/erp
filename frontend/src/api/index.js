import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

// Attachment API
export const attachmentApi = {
  listByEntity: (entityType, entityId) =>
    api.get(`/attachments/entity/${entityType}/${entityId}/`),
  upload: (entityType, entityId, file, description) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('entity_type', entityType)
    formData.append('entity_id', String(entityId))
    if (description) formData.append('description', description)
    return api.post('/attachments/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  delete: (id) => api.delete(`/attachments/${id}/`),
}

// Foundries API
export const foundryApi = {
  list: (params) => api.get('/foundries/', { params }),
  get: (id) => api.get(`/foundries/${id}/`),
  create: (data) => api.post('/foundries/', data),
  update: (id, data) => api.put(`/foundries/${id}/`, data),
  delete: (id) => api.delete(`/foundries/${id}/`),
  linkCustomer: (foundryId, customerIds) => api.post(`/foundries/${foundryId}/link-customer/`, { customer_ids: customerIds })
}

// Castings API
export const castingApi = {
  list: (params) => api.get('/castings/', { params }),
  get: (id) => api.get(`/castings/${id}/`),
  create: (data) => api.post('/castings/', data),
  update: (id, data) => api.put(`/castings/${id}/`, data),
  delete: (id) => api.delete(`/castings/${id}/`),
  linkToPart: (castingId, partIds) => api.post(`/castings/${castingId}/link-to-part/`, { part_ids: partIds }),
  getLinkedCastings: (customerId, params) => api.get(`/customers/${customerId}/castings/`, { params })
}

// Casting Ins API
export const castingInApi = {
  list: (params) => api.get('/casting-ins/', { params }),
  get: (id) => api.get(`/casting-ins/${id}/`),
  create: (data) => api.post('/casting-ins/', data),
  update: (id, data) => api.put(`/casting-ins/${id}/`, data),
  delete: (id) => api.delete(`/casting-ins/${id}/`),
  upload: (formData) => api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// Workpiece Outs API
export const workpieceOutApi = {
  list: (params) => api.get('/workpiece-outs/', { params }),
  get: (id) => api.get(`/workpiece-outs/${id}/`),
  create: (data) => api.post('/workpiece-outs/', data),
  update: (id, data) => api.put(`/workpiece-outs/${id}/`, data),
  delete: (id) => api.delete(`/workpiece-outs/${id}/`)
}

// Customers API
export const customersApi = {
  list: (params) => api.get('/customers/', { params }),
  get: (id) => api.get(`/customers/${id}/`),
  create: (data) => api.post('/customers/', data),
  update: (id, data) => api.put(`/customers/${id}/`, data),
  delete: (id) => api.delete(`/customers/${id}/`),
  getLinkedCastings: (customerId, params) => api.get(`/customers/${customerId}/castings/`, { params })
}

// Payment Plans API
export const paymentPlansApi = {
  list: (params) => api.get('/payment-plans/', { params }),
  get: (id) => api.get(`/payment-plans/${id}/`),
  create: (data) => api.post('/payment-plans/', data),
  update: (id, data) => api.put(`/payment-plans/${id}/`, data),
  delete: (id) => api.delete(`/payment-plans/${id}/`),
  recordPayment: (id, data) => api.post(`/payment-plans/${id}/record-payment/`, data),
  getUnalignedPlans: () => api.get('/payment-plans/unaligned-plans/'),
}

// Production Plans API
export const productionPlansApi = {
  list: (params) => api.get('/production-plans/', { params }),
  get: (id) => api.get(`/production-plans/${id}/`),
  create: (data) => api.post('/production-plans/', data),
  update: (id, data) => api.put(`/production-plans/${id}/`, data),
  delete: (id) => api.delete(`/production-plans/${id}/`)
}

// Quality Issues API
export const qualityIssuesApi = {
  list: (params) => api.get('/quality-issues/', { params }),
  get: (id) => api.get(`/quality-issues/${id}/`),
  create: (data) => api.post('/quality-issues/', data),
  update: (id, data) => api.put(`/quality-issues/${id}/`, data),
  delete: (id) => api.delete(`/quality-issues/${id}/`)
}

// Aliases
export const customerApi = customersApi
export const paymentPlanApi = paymentPlansApi
export const qualityIssueApi = qualityIssuesApi
export const partApi = castingApi

// Todos API
export const todosApi = {
  list: () => api.get('/todos/'),
  create: (data) => api.post('/todos/', data),
  update: (id, data) => api.put(`/todos/${id}/`, data),
  delete: (id) => api.delete(`/todos/${id}/`),
  cleanup: () => api.post('/todos/cleanup-checked/'),
}
