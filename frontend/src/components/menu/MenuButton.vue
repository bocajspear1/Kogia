<template>
    <template v-if="!disabled">
      <a class="button is-outlined" @click="buttonClick">
          <span class="icon is-small" :title="tooltip">
              <mdicon :name="iconname" :size="30" />
          </span>
      </a>
    </template>
    <template v-else>
      <span class="button is-outlined" disabled>
        <span class="icon is-small " :title="tooltip">
          <mdicon :name="iconname" :size="30" />
        </span>
      </span>
      
    </template>
      
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
  props: ["iconname", "tooltip", "disabled"],
  mounted() {
    
  },
  methods: {
    buttonClick() {
        this.$emit('click', this.file_list);
    }
  }
}
</script>
