import api from './index'

export const materialInsApi = {
  list: (params) => api.get('/material-ins/', { params }),
  get: (id) => api.get(`/material-ins/${id}/`),
  create: (data) => api.post('/material-ins/', data),
  update: (id, data) => api.put(`/material-ins/${id}/`, data),
  delete: (id) => api.delete(`/material-ins/${id}/`),
  upload: (formData) => api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
