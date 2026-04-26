// User state module
window.WOC_UserStore = {
  user: null,
  setUser: function(u) { this.user = u; },
  getUser: function() { return this.user; }
};
