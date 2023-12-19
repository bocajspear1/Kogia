
<template>
    <template v-if="clickable">
        <a @click="onClick"><img :src="image_src"/></a>
    </template>
    <template v-else>
        <img :src="image_src"/>
    </template>
    
</template>

<style scoped>

</style>

<script>


export default {
 data() {
   return {
     image_src: ""
   }
 },
 props: ['base64Data', 'path', 'name', 'clickable'],
 emits: ['click'],
 computed:{
    hasClickListener(){
        return (this.$attrs && this.$attrs.onClick)
    }
 },
 mounted() {
   if (this.base64Data != "") {
    this.image_src = "data:image/png;base64," + this.base64Data;
   } else {
    this.image_src = this.path;
   }
 },    
 methods: {
   onClick() {
    this.$emit('click', this.name);
   },
 }
}
</script>
