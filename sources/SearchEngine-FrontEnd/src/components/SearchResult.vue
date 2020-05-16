<template>
    <div>
        <div class="searchbox">
            <el-input v-model="searchkey">
                <el-button type="primary" @click="search" slot="append">搜索</el-button>
            </el-input>
        </div>
        <div class="searchresult">
            <template v-for="item in searchresult">
                <div v-bind:key="item.internal_index">
                    <a id="title" v-bind:key="item.internal_index" v-bind:href="detail_url(item.internal_index)" target="_blank" class="title">
                        {{ item.title }}
                    </a>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import { GET } from '../api/index'
export default {
  name: 'searchresult',
  data () {
    return {
      searchkey: '',
      searchresult: []
    }
  },
  created () {
    var key = this.$route.query.searchkey
    GET('/search', {searchkey: key}).then(result => {
      this.searchresult = result
    })
  },
  methods: {
    search () {
      this.$route.query.searchkey = this.searchkey
      GET('/search', {searchkey: this.searchkey}).then(result => {
        this.searchresult = result
      })
    },
    detail_url (index) {
      return 'detail?index=' + String(index)
    }
  }
}
</script>
