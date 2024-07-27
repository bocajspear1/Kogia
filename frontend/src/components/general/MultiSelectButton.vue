
<template>
    <div class="field has-addons">
        <p class="control" v-for="item in items">
            <button :class="current_item == item.value ? 'button is-success' : 'button'" @click="onClick(item.value )">
            <span class="icon is-small" v-if="item['icon'] != null">
                <mdicon :name="item['icon']" />
            </span>&nbsp;
            <span>{{ item['text'] }}</span>
            </button>
        </p>
    </div>
    
</template>

<style scoped>

</style>

<script>


export default {
 data() {
   return {
     current_item: null
   }
 },
 props: ['items'],
 emits: ['click'],
 mounted() {
   this.current_item = this.items[0]['value'];
 },    
 methods: {
   onClick(value) {
    this.$emit('click', value);
    this.current_item = value;
   },
 }
}
</script>
