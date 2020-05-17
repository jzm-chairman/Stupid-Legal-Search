<template>
    <div>
        <p><v-head></v-head></p>
        <router-view></router-view>
    </div>
</template>

<script>
import vHead from './Header.vue'
export default {
  components: {
    vHead
  }
}
</script>
