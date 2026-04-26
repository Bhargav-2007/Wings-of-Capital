// Core Web Vitals tracking (LCP, FID, CLS)
window.WOC_Performance = {
  report: function(metric, value) {
    // Send to backend or log
    console.log('Performance:', metric, value);
  }
};
