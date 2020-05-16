/* eslint-disable prefer-promise-reject-errors */
/* eslint-disable no-console */
import axios from 'axios'

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/',
  timeout: 10000
})

service.interceptors.request.use(config => {
  return config
}, error => {
  console.log(error)
  return Promise.reject()
})

service.interceptors.response.use(response => {
  if (response.status === 200) {
    return response.data
  } else {
    Promise.reject()
  }
}, error => {
  console.log(error)
  return Promise.reject()
})

export default service
