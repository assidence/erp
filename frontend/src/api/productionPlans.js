import api from './index'

export const productionPlansApi = {
  list: (params) => api.get('/production-plans/', { params }),
  get: (id) => api.get(`/production-plans/${id}/`),
  create: (data) => api.post('/production-plans/', data),
  update: (id, data) => api.put(`/production-plans/${id}/`, data),
  delete: (id) => api.delete(`/production-plans/${id}/`)
}
