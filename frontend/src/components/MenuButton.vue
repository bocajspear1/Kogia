<template>
    <a class="button is-outlined" @click="buttonClick">
        <span class="icon is-small">
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
