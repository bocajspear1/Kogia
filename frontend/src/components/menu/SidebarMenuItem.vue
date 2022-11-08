<template>
    <li>
        <a @click="buttonClick" :class="active ? 'sidebar-menu-item is-active' : 'sidebar-menu-item'">
            <span class="icon is-small">
                <mdicon :name="iconname" :size="30" />
            </span>&nbsp;&nbsp;
            <slot></slot>
        </a>
    </li>
</template>

<style scoped>
.sidebar-menu-item {
    padding: 15px;
}
</style>

<script>
export default {
  data() {
    return {
      
    }
  },
  emits: ['click'],
  props: {
    "iconname": String,
    "active": Boolean
  },
  mounted() {

  },
  methods: {
    buttonClick() {
        this.$emit('click');
    }
  }
}
</script>
