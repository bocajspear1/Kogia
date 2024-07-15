<template>
    <ul>
        <li v-for="page in pages">
            <template v-if="page.path == ''">
                {{ page.title }}
                <NestedMenu 
                v-if="page.subpaths.length > 0"
                :key="page.subpaths.path"
                :pages="page.subpaths"
                />
                
            </template>
            <template v-else>
                <router-link :to="page.path">{{ page.title }}</router-link>
            </template>
            
        </li>
    </ul>
</template>

<style scoped>

</style>

<script>
export default {
  name: "NestedMenu",
  data() {
    return {
      
    }
  },
  props: ['pages'],
  mounted() {
    
  },
  methods: {
        
  }
}
</script>
