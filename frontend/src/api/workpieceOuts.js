import api from './index'

export const workpieceOutApi = {
  list: (params) => api.get('/workpiece-outs/', { params }),
  get: (id) => api.get(`/workpiece-outs/${id}/`),
  create: (data) => api.post('/workpiece-outs/', data),
  update: (id, data) => api.put(`/workpiece-outs/${id}/`, data),
  delete: (id) => api.delete(`/workpiece-outs/${id}/`)
}