/**
 * JobGuard AI - Toast Notification System
 * 
 * Renders non-blocking, accessible toast notifications with auto-dismissal.
 * 
 * @module ui/toast
 */

export class Toast {
  static timer = null;

  /**
   * Display a toast notification.
   * @param {string} message Text message to display
   * @param {string} [type='info'] Notification type: 'success' | 'warning' | 'error' | 'info'
   * @param {number} [duration=2400] Duration in milliseconds
   */
  static show(message, type = 'info', duration = 2400) {
    const toastEl = document.getElementById('toast');
    const toastText = document.getElementById('toastText');

    if (toastEl && toastText) {
      toastText.textContent = message;
      toastEl.classList.add('show');

      if (this.timer) {
        clearTimeout(this.timer);
      }

      this.timer = setTimeout(() => {
        toastEl.classList.remove('show');
      }, duration);
      return;
    }

    // Dynamic fallback if static element is absent
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 300);
    }, duration);
  }

  static success(msg, duration) {
    this.show(msg, 'success', duration);
  }

  static error(msg, duration) {
    this.show(msg, 'error', duration);
  }

  static warning(msg, duration) {
    this.show(msg, 'warning', duration);
  }

  static info(msg, duration) {
    this.show(msg, 'info', duration);
  }
}
