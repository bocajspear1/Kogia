<template>
    <div class="level m-2" v-if="data != null">
        <div v-for="item in data" class="level-item has-text-centered">
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

export default {
  data() {
    return {
    }
  },
  props: ["data"],
  mounted() {
    console.log("GenericDataBar loaded")
    console.log(this.plugin_name);
    console.log(this.data);
  },
  methods: {
    
  }
}
</script>
