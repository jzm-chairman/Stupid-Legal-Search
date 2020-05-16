<template>
    <div>
        <div class="searchbox">
            <el-input v-model="searchkey">
                <el-button type="primary" @click="link" slot="append">搜索</el-button>
            </el-input>
        </div>
    </div>
</template>

<script>
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
    }
  }
}
</script>
