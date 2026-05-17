import api from './index'

export const partsApi = {
  list: (params) => api.get('/parts/', { params }),
  get: (id) => api.get(`/parts/${id}/`),
  create: (data) => api.post('/parts/', data),
  update: (id, data) => api.put(`/parts/${id}/`, data),
  delete: (id) => api.delete(`/parts/${id}/`)
}
