// Prevent flash of unstyled content by applying theme immediately - TAILWIND v4 COMPATIBLE
(function() {
  try {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    
    console.log('⚡ [THEME INIT] Initializing with:', initialTheme);
    
    // Remove any existing dark class
    document.documentElement.classList.remove('dark');
    
    // Only add 'dark' class if theme is dark (Tailwind v4 default behavior)
    if (initialTheme === 'dark') {
      document.documentElement.classList.add('dark');
    }
    
    document.documentElement.setAttribute('data-theme', initialTheme);
    
    // FORCE apply CSS variables immediately
    if (initialTheme === 'dark') {
      document.documentElement.style.setProperty('--background', '#0f172a', 'important');
      document.documentElement.style.setProperty('--foreground', '#f8fafc', 'important');
    } else {
      document.documentElement.style.setProperty('--background', '#ffffff');
      document.documentElement.style.setProperty('--foreground', '#171717');
    }
    
    localStorage.setItem('theme', initialTheme);
    
    console.log('✅ [THEME INIT] Applied successfully. HTML class:', document.documentElement.className);
    console.log('✅ [THEME INIT] Has dark class:', document.documentElement.classList.contains('dark'));
  } catch (error) {
    console.error('❌ [THEME INIT] Failed:', error);
  }
})();
