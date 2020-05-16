import request from './request'

export const GET = (url, data) => {
  url = url + '?' + Array.from(Object.entries(data), item => item.join('=')).join('&')
  console.log(url)
  return request({
    url: url,
    method: 'get'
  })
}
