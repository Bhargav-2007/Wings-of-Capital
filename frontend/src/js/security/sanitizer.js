// Simple DOM sanitizer (for demo, use DOMPurify in prod)
window.WOC_Sanitize = function(str) {
  return String(str).replace(/[<>]/g, '');
};
