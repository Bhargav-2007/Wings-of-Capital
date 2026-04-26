// Focus trap for modals
window.WOC_FocusTrap = {
  trap: function(modal) {
    // Implement focus trap logic
    // For demo: focus first input
    const input = modal.querySelector('input,button,select,textarea');
    if (input) input.focus();
  }
};
