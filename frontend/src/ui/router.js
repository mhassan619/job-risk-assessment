/**
 * JobGuard AI - Single Page Router & Navigation Controller
 * 
 * Manages view transitions between SPA screens, updates sidebar active states,
 * and executes page entry/exit lifecycle hooks.
 * 
 * @module ui/router
 */

export class Router {
  static currentPage = 'new-analysis';
  static listeners = {};

  /**
   * Register a callback for a specific page route transition.
   * @param {string} pageKey e.g. 'history', 'insights', 'new-analysis'
   * @param {Function} callback 
   */
  static on(pageKey, callback) {
    if (!this.listeners[pageKey]) {
      this.listeners[pageKey] = [];
    }
    this.listeners[pageKey].push(callback);
  }

  /**
   * Navigate to a target page view by Key (e.g. 'new-analysis', 'history', 'results', 'loading').
   * @param {string} pageKey 
   */
  static navigate(pageKey) {
    const cleanKey = pageKey.replace(/^page-/, '');
    const targetId = `page-${cleanKey}`;

    const pages = document.querySelectorAll('.page');
    let targetFound = false;

    pages.forEach((page) => {
      if (page.id === targetId || page.id === cleanKey) {
        page.classList.add('active');
        targetFound = true;
      } else {
        page.classList.remove('active');
      }
    });

    if (!targetFound) {
      console.warn(`Router: Target page "${targetId}" not found.`);
      return;
    }

    this.currentPage = cleanKey;

    // Update navigation items in sidebar
    const navItems = document.querySelectorAll('.nav-item[data-page]');
    navItems.forEach((item) => {
      if (item.dataset.page === cleanKey) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Close mobile drawer if open
    this.closeSidebar();

    // Trigger registered page lifecycle hooks
    if (this.listeners[cleanKey]) {
      this.listeners[cleanKey].forEach((fn) => {
        try {
          fn(cleanKey);
        } catch (err) {
          console.error(`Router: Error in route handler for ${cleanKey}:`, err);
        }
      });
    }

    // Scroll content container back to top
    const contentArea = document.querySelector('.content');
    if (contentArea) {
      contentArea.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
    }
  }

  static openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar) sidebar.classList.add('open');
    if (overlay) overlay.classList.add('open');
  }

  static closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
  }

  /**
   * Initialize navigation event handlers on all nav links and buttons.
   */
  static init() {
    const navItems = document.querySelectorAll('.nav-item[data-page]');
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        this.navigate(item.dataset.page);
      });
    });

    // Mobile sidebar hamburger & overlay
    const menuToggle = document.getElementById('menuToggle');
    const overlay = document.getElementById('overlay');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
      menuToggle.addEventListener('click', () => {
        sidebar.classList.contains('open') ? this.closeSidebar() : this.openSidebar();
      });
    }

    if (overlay) {
      overlay.addEventListener('click', () => this.closeSidebar());
    }

    // Back to new analysis button
    const backBtn = document.getElementById('backToNew');
    if (backBtn) {
      backBtn.addEventListener('click', () => this.navigate('new-analysis'));
    }
  }
}
