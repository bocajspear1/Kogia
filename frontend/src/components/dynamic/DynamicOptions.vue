<script setup>

</script>

<template>
    <template v-for="option in options">
        <div v-if="option.type == 'number' || option.type == 'int'" class="field">
            <label class="label">{{ option.description }}</label>
            <div class="control">
                <input class="input short-textbox" type="text" :name="option.name" v-model="option_data[option.name]" size="10" @change="onChange">
            </div>
        </div>
        <div v-if="option.type == 'string'" class="field">
            <label class="label">{{ option.description }}</label>
            <div class="control">
                <input class="input" type="text" :name="option.name" v-model="option_data[option.name]" @change="onChange">
            </div>
        </div>
        <div v-if="option.type == 'textarea'" class="field">
            <label class="label">{{ option.description }}</label>
            <div class="control">
                <textarea class="textarea" v-model="option_data[option.name]"  @change="onChange"></textarea>
            </div>
        </div>
        <div v-if="option.type == 'select'" class="field">
            <label class="label">{{ option.description }}</label>
            
            <div class="control">
                <div class="select">
                    <select v-model="option_data[option.name]"  @change="onChange">
                        <template v-for="selection in option.selections">
                            <template v-if="selection==option.default">
                            <option :value="selection" selected>{{ selection }}</option>
                            </template>
                            <template v-else>
                            <option :value="selection">{{ selection }}</option>
                            </template>
                        </template>
                    </select>
                </div>
            </div>
        </div>
        <div v-if="option.type == 'multistring'" class="field">
            <label class="label">{{ option.description }}</label>
            <ul class="multistring-list">
                <li v-for="(multival, index) in multi_strings[option.name]">
                    <div class="control" >
                        <input class="input" type="text" v-model="multi_strings[option.name][index]" @focusout="onMultiListChange(option.name)">
                    </div>
                </li>
                <li class="control">
                    <div class="control" >
                        <input class="input" type="text" @focusout="onMultiAddChange(option.name, $event.target.value)" :ref="option.name">
                    </div>
                </li>
            </ul>
        </div>
    </template>
   
</template>

<style scoped>
.multistring-list > li > div  {
    display: inline-block;
    vertical-align: middle;
    width: 100%;

}
</style>

<script>

export default {
  data() {
    return {
        option_data: {},
        multi_strings: {}
    }
  },
  props: {
    options: Object,
  },
  emits: ["onOptionChange"],
  mounted() {
    this._updateOptions();
  },
  watch: {
    'options' (to, from) {
        this._updateOptions();
    }
  },
  computed: {
    
  },
  methods: {
    _updateOptions() {
        for (var i in this.options) {
            
            if (this.options[i].type == 'multistring') {
                this.multi_strings[this.options[i].name] = [this.options[i].default];
                this.option_data[this.options[i].name] = [this.options[i].default];
            } else {
                this.option_data[this.options[i].name] = this.options[i].default;
            }
        }
        this.$emit('onOptionChange', this.option_data);
    },
    onChange() {
        this.$emit('onOptionChange', this.option_data);
    },
    onMultiAddChange(option_name, new_value) {

        if (new_value != '') {
            this.multi_strings[option_name].push(new_value);
            this.$refs[option_name][0].value = '';
            this.option_data[option_name] = this.multi_strings[option_name];
            this.$emit('onOptionChange', this.option_data);
        }
        
    },
    onMultiListChange(option_name) {

        for (var i in this.multi_strings[option_name]) {
            if (this.multi_strings[option_name][i] == '') {
                this.multi_strings[option_name].splice(i, 1);
            }
        }
        this.option_data[option_name] = this.multi_strings[option_name];
        this.$emit('onOptionChange', this.option_data);
    }
  }
}
</script>