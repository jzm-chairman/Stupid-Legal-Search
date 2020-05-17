<template>
    <div>
        <div class="filters">
            <ul>
                <li class="filters-item" v-for="(value,key) in filters" :key="key">
                    {{ key }} = {{ value }}
                    <span class="filters-icon" @click="remove_filter(key)"><i class="el-icon-close"></i></span>
                </li>
            </ul>
        </div>
        <div class="sidebar">
            <el-menu
            class="sidebar-menu"
            unique-opened>
                <template v-for="(stat_value,stat_key) in statistics">
                    <el-submenu :index="stat_key" :key="stat_key">
                        <template slot="title">
                            {{ stat_key }}
                        </template>
                        <template v-for="(count,item) in stat_value">
                            <el-menu-item @click.native="add_filter(stat_key, item)" :index="item" :key="item">
                                {{ item }}({{ count }})
                            </el-menu-item>
                        </template>
                    </el-submenu>
                </template>
            </el-menu>
        </div>
        <div class="right">
            <div class="searchbox">
                <el-input v-model="filters.searchkey">
                    <el-button type="primary" @click="search" slot="append">搜索</el-button>
                </el-input>
            </div>
            <div class="searchresult">
                <template v-for="item in searchresult">
                    <div v-bind:key="item.index">
                        <a id="title" v-bind:key="item.index" v-bind:href="detail_url(item.index)" target="_blank" class="title">
                            {{ item.文首 }}
                        </a>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import { GET } from '../api/index'
import merge from 'webpack-merge'
export default {
  name: 'searchresult',
  data () {
    return {
      searchresult: [],
      statistics: {},
      filters: {
        searchkey: ''
      }
    }
  },
  created () {
    this.filters = this.$route.query
    GET('/search', this.filters).then(response => {
      this.searchresult = response.results
      this.statistics = response.statistics
    })
  },
  computed: {
  },
  methods: {
    search () {
      console.log(this.$route.query, this.filters)
      this.$router.push({query: merge(this.$route.query, this.filters)})
      GET('/search', this.filters).then(response => {
        this.searchresult = response.results
        this.statistics = response.statistics
      })
    },
    detail_url (index) {
      return 'detail?index=' + String(index)
    },
    add_filter (key, value) {
      this.filters[key] = value
      this.search()
    },
    remove_filter (key) {
      if (key !== 'searchkey') {
        delete this.filters[key]
      }
      this.$router.push({query: {}})
      this.search()
    }
  }
}
</script>

<style scoped>
.filters {
        position: relative;
        height: 50px;
        overflow: hidden;
        background: #fff;
}
.filters ul {
        box-sizing: border-box;
        width: 100%;
        height: 100%;
}
.filters-item {
        float: left;
        margin: 3px 5px 2px 3px;
        border-radius: 3px;
        font-size: 12px;
        overflow: hidden;
        cursor: pointer;
        height: 23px;
        line-height: 23px;
        border: 1px solid #e9eaec;
        background: #fff;
        padding: 0 5px 0 12px;
        vertical-align: middle;
        color: #666;
    }
.sidebar {
    left: 0;
    float: left;
}
.sidebar-menu {

}
.right {
    float: right;
}
</style>
