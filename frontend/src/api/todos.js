import api from './index'

export const todosApi = {
  list: () => api.get('/todos/'),
  create: (data) => api.post('/todos/', data),
  update: (id, data) => api.put(`/todos/${id}/`, data),
  delete: (id) => api.delete(`/todos/${id}/`),
  cleanup: () => api.post('/todos/cleanup-checked/'),
}
