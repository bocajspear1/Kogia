<script setup>
import NestedMenu from '@/components/general/NestedMenu.vue';
</script>
    
<template>

<div class="column is-2 p-3 content mt-4">
  <NestedMenu :pages="navigation"></NestedMenu>
</div>
<div class="container column is-10 content mt-4" id="">
  <VueShowdown
    :markdown="page_content"
    flavor="github"
    :options="{ emoji: true }"
  />
</div>

   
</template>

<style>

</style>

<script>

import api from "@/lib/api";

function capFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function setPaths(items) {
  var return_items = []
  for (var i in items) {
      var item = items[i];
      var index = false;
      if (item['path'].endsWith('index')) {
        index = true;
      }
      if (item['path'] != '') {
        item['path'] = "/userguide/" + item['path'];
      }
      if (item['subpaths'] && item['subpaths'].length > 0) {
        item['subpaths'] = setPaths(item['subpaths']);
      }
      if (!index) {
        return_items.push(item);
      } else {
        return_items.unshift(item);
      }
      
  }
  return return_items;
}

export default {
  data() {
    return {
        page_content: '',
        navigation: []
    }
  },

  mounted() {
    this.updatePage();
  },
  watch: {
    '$route' (to, from) {
        this.updatePage();
    }
  },
  methods: {
    updatePage() {
      var self = this;
      var my_page = this.$route.params.page;
      if (!my_page) {
        my_page = ["index"];
      }
      my_page = my_page.join("/")
      console.log(my_page)
      api.get_docs_page(my_page, function(resp_data){

        // Update branding
        var content = resp_data['page'];
        content = content.replace(/kogia/g, import.meta.env.VITE_IMAGE_PREFIX);
        var uncapped = import.meta.env.VITE_IMAGE_PREFIX;
        content = content.replace(/Kogia/g, capFirst(uncapped));

        // Update links
        content = content.replace(/\(([-a-zA-Z0-9_/]+)\.md\)/g, "($1)");

        // Update images
        content = content.replace(/\((\/images\/.*)\)/g, "(/api/v1/docs$1)");
          
        self.page_content = content;

        self.navigation = [];
        self.navigation = setPaths(resp_data['navigation']);
        
        
      },
      function(status, data){
        self.page_content = "# 404 Page not Found";
      })
    }
  }
}
</script>