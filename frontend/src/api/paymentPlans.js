import api from './index'

export const paymentPlansApi = {
  list: (params) => api.get('/payment-plans/', { params }),
  get: (id) => api.get(`/payment-plans/${id}/`),
  create: (data) => api.post('/payment-plans/', data),
  update: (id, data) => api.put(`/payment-plans/${id}/`, data),
  delete: (id) => api.delete(`/payment-plans/${id}/`)
}
