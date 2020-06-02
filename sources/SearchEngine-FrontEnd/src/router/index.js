import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      name: 'Home',
      component: () => import('../components/Home.vue'),
      meta: { title: '菜鸡的搜索' }
    },
    {
      path: '/',
      name: 'Common',
      component: () => import('../common/Common.vue'),
      children: [
        {
          path: '/result',
          name: 'SearchResult',
          component: () => import('../components/SearchResult.vue'),
          meta: { title: '搜索结果' }
        },
        {
          path: '/detail',
          name: 'Detail',
          component: () => import('../components/Detail.vue'),
          meta: { title: '文书细节' }
        }
      ]
    }
  ]
})
