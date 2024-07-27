<script setup>
import Paginator from '@/components/general/Paginator.vue'
</script>

<template>
    <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <th v-if="selectable" class="select-column">Select</th>
                <th v-for="column in columns">
                    {{ column }}
                    <span v-if="!limitFilter.hasOwnProperty(column) && (column.toLowerCase() != 'id' || column.toLowerCase() != 'uuid') && !noFilter.includes(column)">
                        <input class="input is-info" type="text" @input="event => newFilter(column, event.target.value)"/>
                    </span>
                    <div v-if="limitFilter.hasOwnProperty(column)" class="select is-fullwidth">
                        <select>
                            <option selected>Filter {{ column }}</option>
                            <template v-for="value in limitFilter[column]">    
                            <option @click="newFilter(column, value)">{{ value }}</option>
                            </template>
                        </select>
                    </div>
                </th>
            </tr>
            <tr>
                <td :colspan="getColCount">
                    <Paginator :item_total="totalItems" :page_size="pageSize" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td :colspan="getColCount">
                    <Paginator :item_total="totalItems" :page_size="pageSize" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
        </tfoot>

        <tbody>
            <tr v-if="loading">
                <td :colspan="getColCount">
                    <div class="container p-3">
                        <progress class="progress is-medium is-info" max="100">50%</progress>
                    </div>
                </td>
            </tr>
            
            <template v-if="data.length > 0" >
                
                <tr v-for="row in data">
                    <td v-if="selectable" class="select-column">
                        <input type="checkbox" v-model="item_map[row[select_column]]" @input="checkClicked(row[select_column], $event.target.checked)" >
                    </td>
                    <td class="allow-newlines" v-for="(column, index) in columns">
                        {{ row[index] }}
                    </td>
                </tr>
            </template>
            <template v-else-if="data.length == 0 && !loading" >
                <tr>
                    <td :colspan="getColCount" >
                        <div class="notification is-warning">
                            No results found
                        </div>
                    </td>
                </tr>
            </template>
        </tbody>
    </table>

   
</template>

<style scoped>
    .allow-newlines {
        white-space: pre-wrap; 
    }
    .select-column {
        width: 20px;
        text-align: center;
    }
</style>

<script>

export default {
  data() {
    return {
        page: 0,
        current_page: 1,
        item_map: {}
    }
  },
  props: {
    columns: Array,
    data: Array,
    pageSize: Number,
    totalItems: Number,
    noFilter: {
        type: Array,
        default: []
    },
    limitFilter: {
        type: Object,
        default: {}
    },
    selectable: Boolean,
    select_column: Number,
    loading: {
        type: Boolean,
        default: false
    },
  },
  emits: ["onFilter", "onNewPage", "onItemSelect"],
  mounted() {
    
  },
  computed: {
    getColCount(){
        if (!this.selectable) {
            return this.columns.length;
        } else {
            return this.columns.length+1;
        }
    },
  },
  methods: {
    newFilter: function(column, new_filter) {
        console.log("new filter")
        this.current_page = 1;
        this.$emit("onFilter", column, new_filter);
    },
    onNewPage: function(new_page) {
        this.current_page = new_page;
        this.$emit("onNewPage", new_page);
    },
    checkClicked(row_item, value) {
        this.$emit("onItemSelect", row_item, value);
    }
  }
}
</script>