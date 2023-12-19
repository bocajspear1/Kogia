
<template>
    <nav class="pagination is-centered" role="navigation" aria-label="pagination">
        <template v-if="current_page > 1">
            <a class="pagination-previous" @click="lastPage">&lt;</a>
        </template>
        <template v-if="current_page == 1">
            <a class="pagination-previous" disabled>&lt;</a>
        </template>
        <template v-if="current_page < page_count">
            <a class="pagination-next" @click="nextPage">&gt;</a>
        </template>
        <template v-if="current_page == page_count">
            <a class="pagination-next" disabled>&gt;</a>
        </template>


        <ul class="pagination-list">
            <li><a :class="current_page == 1 ? 'is-current pagination-link' : 'pagination-link'" @click="navToPage(1)">1</a></li>
            <li v-if="page_count > 4 && current_page > 3"><span class="pagination-ellipsis">&hellip;</span></li>
            <li><a class="pagination-link" v-if="current_page == page_count && page_count > 3" @click="navToPage(current_page-2)">{{ current_page - 2 }}</a></li>
            <li><a class="pagination-link" v-if="current_page > 2 " @click="navToPage(current_page-1)">{{ current_page - 1 }}</a></li>
            <li><a class="is-current pagination-link" v-if="current_page != 1 && current_page != page_count">{{ current_page }}</a></li>
            <li><a class="pagination-link" v-if="current_page < (page_count - 1) " @click="navToPage(current_page+1)">{{ current_page + 1 }}</a></li>
            <li><a class="pagination-link" v-if="current_page == 1 && page_count > 3" @click="navToPage(current_page+2)">{{ current_page + 2 }}</a></li>
            <li v-if="page_count > 4 && current_page < (page_count - 2)"><span class="pagination-ellipsis">&hellip;</span></li>
            <li><a :class="current_page == page_count ? 'is-current pagination-link' : 'pagination-link'" @click="navToPage(page_count)" v-if="page_count > 1">{{ page_count }}</a></li>
        </ul>
    </nav> 
</template>

<style scoped>

</style>

<script>


export default {
  data() {
    return {
      page_count: 0,
      current_page: 1,
      did_update: false
    }
  },
  watch: {
    'item_total' (to, from) {
        this._updatePageCount();
        this.current_page = 1;
        this.$emit('new_page', 1);
    },
    'sync_page' (to, from) {
        if (!this.did_update) { 
            this.current_page = to;  
        }
        this.did_update = false;
    }
  },
  props: ['item_total', 'page_size', "sync_page"],
  emits: ['new_page'],
  mounted() {
    this._updatePageCount();
  },
  methods: {
    _updatePageCount() {
        this.page_count = Math.ceil(this.item_total / this.page_size);
    },
    nextPage() {
        if (this.current_page < this.page_count) {
            this.navToPage(this.current_page+1)
        }
    },
    lastPage() {
        if (this.current_page > 1) {
            this.navToPage(this.current_page-1)
        }
    },
    navToPage(page_num) {
        this.current_page = page_num;
        this.did_update = true;
        this.$emit('new_page', page_num);
    },
  }
}
</script>
