export const replaceAll = (str, from, to) => {
  var reg = new RegExp(from, 'g')
  return str.replace(reg, to)
}
