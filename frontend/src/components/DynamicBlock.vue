<template>
    <component
        :key="index"
        :is="schema.type"
        :value="data[schema.state]"
        @input="updateData(schema.state, $event)"
        v-bind="schema"
        :data="data"
      >
</template>

<style scoped>

</style>

<script>
import GenericDataBar from '@/components/generic/GenericDataBar.vue'
import GenericListfrom from '@/components/generic/GenericList.vue'

export default {
  data() {
    return {
      
    }
  },
  props: ["dynamic_items"],
  mounted() {
    console.log(this.dynamic_items)
  },
  methods: {
    fileCount() {
      return this.submission.files.length;
    }
  }
}
</script>
