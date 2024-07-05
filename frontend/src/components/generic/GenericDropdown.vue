<template>
<div class="dropdown" ref="dropdownClass">
    <div class="dropdown-trigger">
        <button :class="getColorClass" aria-haspopup="true" aria-controls="dropdown-menu" @click="onClick">
            <slot name="selected" :selected="selected"></slot>
            <span class="icon is-small">
                <mdicon name="chevron-down" :size="30" />
            </span>
        </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu" role="menu">
        <div class="dropdown-content">
            <slot name="dropcontent" :onSelect="onSelect"></slot>   
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
        selected: null
    }
  },
  expose: ['clear'],
  emits: ["item_selected"],
  props: {
    initSelect: null,
    colorClass: {
        type: String,
        default: "is-info"
    }
  },
  mounted() {
    document.getElementsByTagName("html")[0].addEventListener("click", this._clickOut);
    if (this.initSelect) {
        this.selected = this.initSelect;
    }
    
  },
  unmounted() {
    document.getElementsByTagName("html")[0].removeEventListener("click", this._clickOut);
  },
  computed: {
    getColorClass() {
        return "button " + this.colorClass + " is-light";
    }
  },
  methods: {
    _hasRef(){
        return 'dropdownClass' in this.$refs;
    },
    _close() {
        var self = this;
        if (self.active) {
            if(this._hasRef()) {
                self.$refs['dropdownClass'].classList.remove('is-active');
            }
            
            self.active = false;
        } 
    },
    _open() {
        var self = this;
        if (!self.active) {
            if(this._hasRef()) {
                this.$refs['dropdownClass'].classList.add('is-active');
            }
            this.active = true;
        }
    },
    _clickOut(e) {
        var self = this;
        if (self.$refs['dropdownClass'].contains(e.target)) {
            return;
        }
        self._close();
    },
    _toggle() {
        if (this.active) {
            this.$refs['dropdownClass'].classList.remove('is-active');
            this.active = false;
        } else {
            this.$refs['dropdownClass'].classList.add('is-active');
            this.active = true;
        }
    },
    onClick() {
        if (this.active) {
            this._close();
        } else {
            this._open();
        }
    },
    onSelect(item) {
        this.selected = item;
        this.$emit('item_selected', item);
        this._close();
    },
    clear() {
        this.selected = null;
    }
  }
}
</script>