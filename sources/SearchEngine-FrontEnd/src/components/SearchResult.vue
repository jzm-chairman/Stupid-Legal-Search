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
                <el-autocomplete style="width:100%"
                  v-model="filters.searchkey"
                  @keyup.enter.native="search"
                  :trigger-on-focus="false"
                  :fetch-suggestions="prompt"
                  @select="handle_select">
                    <el-button type="primary" @click="search" slot="append">搜索</el-button>
                </el-autocomplete>
            </div>
            <div class="search-result">
                <template v-for="item in searchresult">
                    <div class="search-item" v-bind:key="item.index">
                      <div class="item-title">
                        <a id="title" v-bind:key="item.index" v-bind:href="detail_url(item.index)" target="_blank" class="title">
                            {{ item.文首 }}
                        </a>
                      </div>
                      <div class="item-summary" v-html="item.摘要"></div>
                    </div>
                </template>
            </div>
            <div class="pagination">
              <el-pagination
                layout="total, sizes, prev, pager, next, jumper"
                :page-sizes="[10,20,50,100]"
                :page-size="pagesize"
                :current-page="pageindex"
                :total="total"
                background
                @size-change="change_page_size"
                @current-change="change_page_index"
              ></el-pagination>
            </div>
        </div>
    </div>
</template>

<script>
import { GET } from '../api/index'
import merge from 'webpack-merge'
import { replaceAll } from '../api/utils'
export default {
  name: 'searchresult',
  data () {
    return {
      searchresult: [],
      statistics: {},
      filters: {
        searchkey: ''
      },
      prompt_list: [],
      searchkeycut: '',
      total: 0,
      pageindex: 1,
      pagesize: 10
    }
  },
  created () {
    this.filters = this.$route.query
    this.fetch_data()
  },
  computed: {
  },
  methods: {
    fetch_data () {
      var params = JSON.parse(JSON.stringify(this.filters))
      params.pageindex = this.pageindex
      params.pagesize = this.pagesize
      GET('/search', params).then(response => {
        this.searchresult = response.results
        this.statistics = response.statistics
        this.total = response.total
        this.searchkeycut = response.query_words
        for (var i in this.searchresult) {
          this.searchresult[i].摘要 = this.render(this.searchresult[i].摘要)
        }
      })
    },
    search () {
      console.log(this.$route.query, this.filters)
      this.pageindex = 1
      if (this.$route.query !== this.filters) {
        this.$router.push({query: merge(this.$route.query, this.filters)})
      }
      this.fetch_data()
    },
    detail_url (index) {
      return 'detail?index=' + String(index) + '&searchkey=' + this.filters.searchkey
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
    },
    change_page_size (val) {
      this.pagesize = val
      this.fetch_data()
    },
    change_page_index (val) {
      this.pageindex = val
      this.fetch_data()
    },
    render (summary) {
      for (var i in this.searchkeycut) {
        var word = this.searchkeycut[i]
        summary = replaceAll(summary, word, '<span style="color:red">' + word + '</span>')
      }
      return summary
    },
    prompt (input, callback) {
      GET('/recommend', { prefix: input }).then(response => {
        this.prompt_list = []
        for (var i in response.result) {
          this.prompt_list.push({value: response.result[i]})
        }
        callback(this.prompt_list)
        console.log(this.prompt_list)
      })
    },
    handle_select (item) {
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
    float: left;
    padding: 0 0 0 10px;
}
.sidebar-menu {
  width: 300px;
}
.right {
  float: right;
  padding: 0 100px 0 0;
  width: 60%;
}
.search-item {
  padding: 10px;
}
.search-result {
  padding: 20px;
}
</style>
