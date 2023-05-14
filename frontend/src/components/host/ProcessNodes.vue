<script setup>

</script>
<template>


<ul class="menu-list">
    <li v-for="process in processes">
        <a @click="itemSelected(process)" :class="isActive(process.uuid)"><mdicon name="cog-box" :size="25" />&nbsp;
          <span class="pathtext">{{ process.path }}</span> ({{ process.pid }})
        </a>
        <ProcessNode 
        v-if="process.child_processes.length > 0"
        :key="process.child_processes.id"
        :processes="process.child_processes"
        @child_selected="childSelected"
        :selected_process="selected_process"
        />
    </li>
</ul>
</template>

<style scoped>
  .pathtext{
    font-family: 'Courier New', Courier, monospace;
  }
</style>

<script>
export default {
  name: "ProcessNode",
  props: {
    processes: {
      type: Array,
      required: true
    },
    selected_process: {
      type: String,
    },
  },
  emits: ["child_selected"],
  mounted() {
    var self = this;
  },
  methods: {
    childSelected(child) {
      this.$emit('child_selected', child);
    },
    itemSelected(child) {
      this.$emit('child_selected', child);
    },
    isActive(uuid) {
      if (uuid == this.selected_process) {
        return "is-active";
      } else {
        return "";
      }
    }
  },
}
</script>
