import api from './index'

export const castingApi = {
  list: (params) => api.get('/castings/', { params }),
  get: (id) => api.get(`/castings/${id}/`),
  create: (data) => api.post('/castings/', data),
  update: (id, data) => api.put(`/castings/${id}/`, data),
  delete: (id) => api.delete(`/castings/${id}/`)
}