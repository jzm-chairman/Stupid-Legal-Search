<template>
    <div class="wrap">
        <div class="searchbox">
            <el-autocomplete style="width:100%"
            v-model="searchkey"
            @keyup.enter.native="link"
            :trigger-on-focus="false"
            :fetch-suggestions="prompt"
            @select="link"
            >
              <el-button type="primary" @click="link" slot="append">搜索</el-button>
            </el-autocomplete>
        </div>
    </div>
</template>

<script>
import { GET } from '../api/index'
export default {
  name: 'home',
  data () {
    return {
      searchkey: ''
    }
  },
  methods: {
    link () {
      this.$router.push({path: '/result', query: {searchkey: this.searchkey}})
    },
    prompt (input, callback) {
      GET('/recommend_words', { prefix: input }).then(response => {
        this.prompt_list = []
        for (var i in response.result) {
          this.prompt_list.push({value: response.result[i]})
        }
        callback(this.prompt_list)
      })
    }
  }
}
</script>

<style scoped>
.wrap {
  position: relative;
  width: 100%;
  height: 100%;
  background-image: url(../assets/background.jpg);
  background-size: 100%;
  padding: 0px;
}
.searchbox {
  position: absolute;
  left: 25%;
  top: 50%;
  width: 50%;
}
</style>
