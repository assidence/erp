import api from './index'

export const foundryApi = {
  list: (params) => api.get('/foundries/', { params }),
  get: (id) => api.get(`/foundries/${id}/`),
  create: (data) => api.post('/foundries/', data),
  update: (id, data) => api.put(`/foundries/${id}/`, data),
  delete: (id) => api.delete(`/foundries/${id}/`)
}