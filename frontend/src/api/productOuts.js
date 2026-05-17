import api from './index'

export const productOutsApi = {
  list: (params) => api.get('/product-outs/', { params }),
  get: (id) => api.get(`/product-outs/${id}/`),
  create: (data) => api.post('/product-outs/', data),
  update: (id, data) => api.put(`/product-outs/${id}/`, data),
  delete: (id) => api.delete(`/product-outs/${id}/`)
}
