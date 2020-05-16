import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../components/Home.vue')
    },
    {
      path: '/result',
      name: 'SearchResult',
      component: () => import('../components/SearchResult.vue')
    },
    {
      path: '/detail',
      name: 'Detail',
      component: () => import('../components/Detail.vue')
    }
  ]
})
