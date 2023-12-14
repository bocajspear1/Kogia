<template>
    <li :class="active ? 'is-active' : ''">
        <a @click="buttonClick">
            <span class="icon is-small">
                <mdicon :name="iconname" :size="30" />
            </span>&nbsp;&nbsp;
            <slot></slot>
        </a>
    </li>
</template>

<style scoped>

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
