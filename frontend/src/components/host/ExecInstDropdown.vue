<script setup>
import GenericDropdown from '@/components/generic/GenericDropdown.vue'
</script>
<template>
<GenericDropdown @item_selected="onSelect" ref="intDropdown">
    <template v-slot:selected="selected">
        <mdicon name="application-braces" :size="25" />&nbsp;
        <span v-if="selected.selected == null" >
            Select Execution Instance
        </span>
        <span v-if="selected.selected != null">
            {{ selected.selected.exec_module }} (Finished: {{ selected.selected.end_time }}, Duration: {{ selected.selected.duration }})
        </span>
    </template>
    <template v-slot:dropcontent="dropcontent">
        <template v-if="instances.length != 0">
        <a v-for="instance in instances" class="dropdown-item" @click="dropcontent.onSelect(instance)">
            <mdicon name="microsoft-windows" :size="25" v-if="instance.run_os=='windows'"/>
            <mdicon name="file-cog" :size="25" v-if="instance.run_os=='linux'"/>
            {{ instance.exec_module }} (Finished: {{ instance.end_time }}, Duration: {{ instance.duration }})
        </a>
        </template>
        <template v-if="instances.length == 0">
            <span class="dropdown-item">No Instances</span>
        </template>
    </template>
</GenericDropdown>
</template>

<style scoped>

</style>

<script>

export default {
  data() {
    return {
        current_instance: null,
    }
  },
  emits: ["execinst_selected"],
  props: {
    instances: Array,
  },
  mounted() {
   
    
  },
  unmounted() {
    
  },
  methods: {
    onSelect(file) {
        console.log(file);
        this.current_instance = file;
        this.$emit('execinst_selected', file);
    }
  }
}
</script>