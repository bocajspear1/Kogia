<template>
    <a class="button is-outlined" @click="buttonClick">
        <span class="icon is-small" :title="tooltip">
            <mdicon :name="iconname" :size="30" />
        </span>
    </a>
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
  props: ["iconname", "tooltip"],
  mounted() {
    
  },
  methods: {
    buttonClick() {
        this.$emit('click', this.file_list);
    }
  }
}
</script>
