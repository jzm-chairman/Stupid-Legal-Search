<template>
    <div class="wrap">
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
