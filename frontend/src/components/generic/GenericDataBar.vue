<template>
    <div class="level m-2">
        <div v-for="item in data_list" class="level-item has-text-centered">
            <div v-for="(value, key) in item">
                <p class="heading">{{ key }}</p>
                <p class="title">{{ value }}</p>
            </div>
        </div>
    </div> 
</template>

<style scoped>

</style>

<script>
import plugin_data from './plugin_data';

export default {
  data() {
    return {
      data_list: [],
      
    }
  },
  props: ["plugin_name", "loadon", "action"],
  mounted() {
    console.log("GenericDataBar loaded")
    console.log(this.plugin_name);
    console.log(this.loadon);
    console.log(this.action);
    if (this.loadon == "load") {
      this.loadData();
    }
  },
  methods: {
    loadData() {
      var self = this;
      plugin_data.get_plugin_action(self.plugin_name, self.action, function(resp_data) {
        console.log(resp_data)
        self.data_list = resp_data;
      }, function(resp){

      })
      
    }
  }
}
</script>
