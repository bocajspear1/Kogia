<template>
    <aside class="menu sidebar-menu has-background-white-bis">
        <ul class="menu-list">
            <slot name="main"></slot>
        </ul>
        
    </aside>
</template>

<style scoped>
.sidebar-menu {
    position: fixed;
    padding: 20px;
    width: inherit;
    height: 100%;
}
</style>

<script>
export default {
  data() {
    return {
      
    }
  },
  emits: [''],
  props: [],
  mounted() {
    
  },
  methods: {
    
  }
}
</script>
