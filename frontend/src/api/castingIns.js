import api from './index'

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