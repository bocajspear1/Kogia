<template>
    <div class="level">
        <div v-for="item in data_list" class="level-item has-text-centered">
            <div>
                <p class="heading">{{ item.key }}</p>
                <p class="title">{{ item.value }}</p>
            </div>
        </div>
    </div> 
</template>

<style scoped>

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      "data_list": []
    }
  },
  props: ["plugin_name", "data_action"],
  mounted() {
    
  },
  methods: {
    doAction() {
      var self = this;

      axios.get("/api/v1/plugin/" + self.plugin_name + "/action/" + self.data_action).then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                self.submission = resp_data['result'];
                var date = new Date(self.submission['submit_time']*1000);
                self.submission['submit_time'] = date.toLocaleString() 
                self.done = true;
            }
            
        }).catch(function(resp){
            console.log('FAILURE!!', resp);
        });
    }
  }
}
</script>
