<template>
    <div>
        {{ detail }}
    </div>
</template>

<script>
import { GET } from '../api/index'
export default {
  name: 'detail',
  data () {
    return {
      detail: null
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
