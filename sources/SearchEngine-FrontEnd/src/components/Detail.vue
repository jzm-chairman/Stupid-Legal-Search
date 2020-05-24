<template>
    <div>
        <div class="title">
            <div v-html="detail.文首"></div>
            <div>
                <span v-html="detail.经办法院"></span>
                <span> | </span>
                <span v-html="detail.案号"></span>
                <span> | </span>
                <span v-html="detail.裁判时间"></span>
            </div>
        </div>
        <div class="content">
            <template v-for="key in showkeys">
                <div v-bind:key="key" v-if="key in detail">
                    <div v-html="key"></div>
                    <div v-html="detail[key]"></div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import { GET } from '../api/index'
export default {
  name: 'detail',
  data () {
    return {
      detail: null,
      showkeys: ['当事人', '当事人段', '诉讼记录', '案件基本情况', '案件基本情况段', '案件事实段', '裁判分析过程', '起诉分析段', '判决结果', '本审判决结果', '文尾'],
      searchcut: ''
    }
  },
  computed: {
  },
  created () {
    GET('/detail', this.$route.query).then(result => {
      this.detail = result
      this.searchcut = result.searchcut
      delete this.detail.searchcut
      for (var i in this.showkeys) {
        var key = this.showkeys[i]
        if (key in this.detail) {
          this.detail[key] = this.render(this.detail[key])
        }
      }
    })
  },
  methods: {
    render (value) {
      value = value.replace(' ', '<br>')
      for (var i in this.searchcut) {
        var word = this.searchcut[i]
        value = value.replace(word, '<span style="color:red">' + word + '</span>')
      }
      return value
    }
  }
}
</script>

<style scoped>
.content {
    text-align: left;
}
</style>
