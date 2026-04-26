// Privacy-first analytics
window.WOC_Analytics = {
  track: function(event, props) {
    // Send to analytics endpoint or log
    console.log('Analytics:', event, props);
  }
};
