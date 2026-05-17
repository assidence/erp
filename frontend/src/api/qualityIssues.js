import api from './index'

export const qualityIssuesApi = {
  list: (params) => api.get('/quality-issues/', { params }),
  get: (id) => api.get(`/quality-issues/${id}/`),
  create: (data) => api.post('/quality-issues/', data),
  update: (id, data) => api.put(`/quality-issues/${id}/`, data),
  delete: (id) => api.delete(`/quality-issues/${id}/`)
}
