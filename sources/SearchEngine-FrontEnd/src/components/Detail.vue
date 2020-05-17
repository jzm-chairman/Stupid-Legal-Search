<template>
    <div>
        <div class="title">
            <div>{{ detail.文首 }}</div>
            <div>
                <span>{{ detail.经办法院}} </span>
                <span> | </span>
                <span>{{ detail.案号 }}</span>
                <span> | </span>
                <span>{{ detail.裁判时间 }}</span>
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
      showkeys: ['当事人', '诉讼记录', '案件基本情况', '裁判分析过程', '判决结果', '本审判决结果', '文尾']
    }
  },
  computed: {
  },
  created () {
    GET('/detail', this.$route.query).then(result => {
      this.detail = result
    })
  }
}
</script>

<style scoped>
.content {
    text-align: left;
}
</style>
