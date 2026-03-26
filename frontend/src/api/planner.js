import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const generatePlan = async (payload) => {
  const response = await api.post('/planner/generate/', payload);
  return response.data;
};
