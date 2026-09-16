/**
 * JobGuard AI - Theme Manager
 * 
 * Manages Dark and Light theme states, system preference synchronization,
 * and persistent storage.
 * 
 * @module ui/themeManager
 */

import { StorageService } from '../services/storageService.js';

export class ThemeManager {
  static THEME_DARK = 'dark';
  static THEME_LIGHT = 'light';

  /**
   * Initialize theme from saved preferences or system preference.
   */
  static init() {
    const saved = StorageService.getTheme();
    if (saved) {
      this.applyTheme(saved);
    } else {
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.applyTheme(prefersDark ? this.THEME_DARK : this.THEME_LIGHT);
    }

    // Attach listeners to theme toggles
    const themeToggleBtn = document.getElementById('themeToggle');
    const darkModeSwitch = document.getElementById('darkModeSwitch');

    if (themeToggleBtn) {
      themeToggleBtn.addEventListener('click', () => this.toggle());
    }

    if (darkModeSwitch) {
      darkModeSwitch.addEventListener('change', (e) => {
        this.applyTheme(e.target.checked ? this.THEME_DARK : this.THEME_LIGHT);
      });
    }
  }

  /**
   * Apply theme to root document and persist in storage.
   * @param {'dark'|'light'} theme 
   */
  static applyTheme(theme) {
    const isDark = (theme === this.THEME_DARK);
    
    if (isDark) {
      document.body.classList.remove('light');
      document.documentElement.setAttribute('data-theme', this.THEME_DARK);
      StorageService.setTheme(this.THEME_DARK);
    } else {
      document.body.classList.add('light');
      document.documentElement.setAttribute('data-theme', this.THEME_LIGHT);
      StorageService.setTheme(this.THEME_LIGHT);
    }

    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
      themeToggleBtn.innerHTML = `<svg class="icon"><use href="#${isDark ? 'i-moon' : 'i-sun'}"/></svg>`;
    }

    const darkModeSwitch = document.getElementById('darkModeSwitch');
    if (darkModeSwitch) {
      darkModeSwitch.checked = isDark;
    }
  }

  /**
   * Toggle between dark and light themes.
   * @returns {'dark'|'light'} new theme
   */
  static toggle() {
    const isLight = document.body.classList.contains('light');
    const nextTheme = isLight ? this.THEME_DARK : this.THEME_LIGHT;
    this.applyTheme(nextTheme);
    return nextTheme;
  }
}
