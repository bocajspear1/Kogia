<script setup>

</script>
<template>
    <template  v-for="severity in severities" >
        <div v-if="severity.count > 0" :class="'message ' + severity.class " :ref="severity.name">
            <div class="message-header">
                <p>{{ severity.name }} ({{ severity.count }})</p>
                <button class="card-header-icon" aria-label="toggle severity" @click="toggleSeverity(severity.num)" :title="'Show/hide ' + severity.name + ' plugin'">
                    <span class="icon">
                        <mdicon name="chevron-down" :size="30" v-if="severity.enabled == true" />
                        <mdicon name="chevron-up" :size="30" v-if="severity.enabled == false" />
                    </span>
                </button>
            </div>
            <div v-if="severity.enabled" class="message-body">
                <div class="list">
                    <template v-for="signature in signatures">
                        <div v-if="signature.severity == severity.num" class="list-item" :ref="signature.uuid">
                        
                            <div class="list-item-image p-2">
                                <mdicon v-if="signature.severity == '1'" name="information-variant" :size="30" />
                                <mdicon v-if="signature.severity == '2'" name="help" :size="30" />
                                <mdicon v-if="signature.severity == '3'" name="alert" :size="30" />
                                <mdicon v-if="signature.severity == '4'" name="alert-octagon" :size="30" />
                            </div>
                            <div class="list-item-content">
                                <div class="list-item-title">{{ signature.name }} ({{ signature.plugin }})</div>
                                <div class="list-item-description">
                                    {{ signature.description }}
                                </div>
                            </div>

                        </div>
                    </template>
                    
                </div>
            </div>
            
        </div>
    </template>
    <div class="notification is-info m-2" v-if="signatures.length == 0">
        No signatures found
    </div>
    
</template>

<style scoped>
    .is-suspicious {
        background-color: rgb(255, 233, 193);
    }

    .is-suspicious .message-header {
        background-color: orangered;
        color: white;
    }
</style>

<script>
export default {
  data() {
    return {
        current: null,
        severities: [
            { "name": "Malicious", "num": "4", "class": "is-danger", "count": 0, "enabled": false},
            { "name": "Suspicious", "num": "3", "class": "is-suspicious", "count": 0, "enabled": false },
            { "name": "Caution", "num": "2", "class": "is-warning", "count": 0, "enabled": false },
            { "name": "Informational", "num": "1", "class": "is-info", "count": 0, "enabled": false },
        ]
    }
  },
  watch: {
    'signatures' (to, from) {
        this.updateCount();
    }
  },
  props: {
    signatures: Array,
  },
  mounted() {
    this.updateCount();
  },
  methods: {
    updateCount() {
        for (var s in this.signatures) {
            for (var i = 0; i < this.severities.length; i++) {
                if (this.severities[i].num == this.signatures[s].severity) {
                    this.severities[i].count += 1;
                }
            }
        }
    },
    toggleSeverity(num) {
        for (var i = 0; i < this.severities.length; i++) {
            if (this.severities[i].num == num) {
                this.severities[i].enabled = !this.severities[i].enabled;
            }
        }
    },
  }
}
</script>