// Timezone-aware date parsing
window.WOC_DateFns = {
  parse: function(str) {
    // Example: parse '31 Mar, 3:20 PM' to Date
    return new Date(Date.parse(str));
  }
};
