// Live region updates for screen readers
window.WOC_LiveRegion = {
  announce: function(msg) {
    let region = document.getElementById('woc-live-region');
    if (!region) {
      region = document.createElement('div');
      region.id = 'woc-live-region';
      region.setAttribute('aria-live', 'polite');
      region.style.position = 'absolute';
      region.style.left = '-9999px';
      document.body.appendChild(region);
    }
    region.textContent = msg;
  }
};
