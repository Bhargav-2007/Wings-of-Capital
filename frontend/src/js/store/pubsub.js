// Simple pub/sub event bus
window.WOC_PubSub = (function() {
  const events = {};
  return {
    subscribe: function(event, cb) {
      events[event] = events[event] || [];
      events[event].push(cb);
    },
    publish: function(event, data) {
      (events[event] || []).forEach(cb => cb(data));
    }
  };
})();
