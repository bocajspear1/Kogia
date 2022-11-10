<template>
    <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <th v-for="column in columns">
                    {{ column }}
                    <span v-if="column.toLowerCase() != 'id' || column.toLowerCase() != 'uuid'">
                        <input class="input is-info" type="text" @input="event => newFilter(column, event.target.value)"/>
                    </span>
                </th>
            </tr>
        </thead>
        <tfoot>
            <nav class="pagination is-centered" role="navigation" aria-label="pagination">
                <a class="pagination-previous">Previous</a>
                <a class="pagination-next">Next page</a>
                <ul class="pagination-list">
                    <li><a class="pagination-link" aria-label="Goto page 1">1</a></li>
                    <li><span class="pagination-ellipsis">&hellip;</span></li>
                    <li><a class="pagination-link" aria-label="Goto page 45">45</a></li>
                    <li><a class="pagination-link is-current" aria-label="Page 46" aria-current="page">46</a></li>
                    <li><a class="pagination-link" aria-label="Goto page 47">47</a></li>
                    <li><span class="pagination-ellipsis">&hellip;</span></li>
                    <li><a class="pagination-link" aria-label="Goto page 86">86</a></li>
                </ul>
            </nav>
        </tfoot>

        <tbody>
            <template v-if="data.length > 0" >
                <tr v-for="row in data">
                    <td v-for="(column, index) in columns">
                        {{ row[index] }}
                    </td>
                </tr>
            </template>
            <template v-else-if="data.length == 0" >
                <tr>
                    <td colspan="{{ column.length }}">
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

</style>

<script>

export default {
  data() {
    return {
        page: 0
    }
  },
  props: {
    columns: Array,
    data: Array,
    pageCount: Number 
  },
  emits: ["onFilter", "newPage"],
  mounted() {
    
  },
  methods: {
    newFilter: function(column, new_filter) {
        this.$emit("onFilter", column, new_filter);
    }
  }
}
</script>