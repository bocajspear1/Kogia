

export default  {
    has_key(obj, key) {
        return obj.hasOwnProperty(key);
        // return (key in Object.keys(obj))
    },
    ensure_key(obj, key, default_val) {
        if (!this.has_key(obj, key)) {
            obj[key] = default_val;
        }
    },
    bytesToGBs(value) {
        return Math.round(value / 10000000) / 100
    }
}