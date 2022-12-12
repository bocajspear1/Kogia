
<template>
     <div class="columns">
        <div class="column is-two-thirds">
            <pre>
{{ hex_data_out }}
            </pre>
        </div>
        <div class="column">
            <pre>
{{ hex_ascii_out }}
            </pre>
        </div>
    </div>
</template>

<style scoped>

</style>

<script>


export default {
  data() {
    return {
      hex_data_out: "",
      hex_ascii_out: ""
    }
  },
  props: {
    hexdata: String,
    width: {
        type: Number,
        default: 32
    }
  },
  emits: [],
  watch: {
    'hexdata' (to, from) {
        this.updateView();
    }
  },
  mounted() {
    this.updateView();
  },    
  methods: {
    updateView() {
        var worker = new Worker(
        `data:text/javascript,
        onmessage = function(event) {
            var hexdata = event.data[0];
            var width = event.data[1];
            var hex_data_out = "";
            var hex_ascii_out = "";

            for (var i = 0; i < hexdata.length/2; i+=2) {
                var byte = hexdata[i] + hexdata[i+1];

                var val = parseInt(byte, 16);
                if (val >= 32 && val <= 126) {
                    hex_ascii_out += String.fromCharCode(val);
                } else {
                    hex_ascii_out += ".";
                }

                if (i % (width) == (width-2)) {
                    hex_data_out += byte + "\\n";
                    hex_ascii_out += "\\n";
                } else {
                    hex_data_out += byte + " ";
                }
            }

            postMessage({
                "hex_data_out": hex_data_out,
                "hex_ascii_out": hex_ascii_out,
            });
        }
        `);
        if (this.hexdata.length % 2 == 0) {
            var self = this;
            worker.onmessage = function(event) {
                self.hex_data_out = event.data['hex_data_out'];
                self.hex_ascii_out = event.data['hex_ascii_out'];
            };
            worker.postMessage([
                self.hexdata,
                self.width
            ]);
        }
    },
  }
}
</script>
