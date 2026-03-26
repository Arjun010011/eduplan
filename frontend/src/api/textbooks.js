import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const fetchTextbooks = async (params) => {
  const response = await api.get('/textbooks/', { params });
  return response.data;
};
