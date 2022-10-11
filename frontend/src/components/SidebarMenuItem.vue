<template>
    <li>
        <a @click="buttonClick" class="sidebar-menu-item">
            <span class="icon is-small" >
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
  props: ["iconname"],
  mounted() {
    console.log(this.iconname)
  },
  methods: {
    buttonClick() {
        this.$emit('click', this.file_list);
    }
  }
}
</script>
