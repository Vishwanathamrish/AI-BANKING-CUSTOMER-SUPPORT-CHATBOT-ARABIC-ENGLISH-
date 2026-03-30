'use client';

import { createContext, useState, useEffect, useContext, ReactNode } from "react";

interface ThemeContextType {
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);
export { ThemeContext };

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  // Start with 'light' (no 'dark' class means light mode)
  const [theme, setThemeState] = useState<'dark' | 'light'>('light');
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize theme from localStorage on mount (client-side only)
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'dark' | 'light' | null;
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Use saved theme if exists, otherwise use system preference
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    
    console.log('🎨 [INIT] Starting theme:', initialTheme);
    console.log('🎨 [INIT] Saved:', savedTheme, 'System dark:', systemPrefersDark);
    
    // CRITICAL: Only add/remove 'dark' class for Tailwind compatibility
    document.documentElement.classList.remove('dark');
    document.body.classList.remove('dark');
    
    if (initialTheme === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
    }
    document.documentElement.setAttribute('data-theme', initialTheme);
    
    // Update state AFTER applying to DOM
    setThemeState(initialTheme);
    localStorage.setItem('theme', initialTheme);
    setIsInitialized(true);
    
    console.log('✅ [INIT] Complete. HTML class:', document.documentElement.className);
    console.log('✅ [INIT] Body class:', document.body.className);
    console.log('✅ [INIT] Theme state:', theme, '→', initialTheme);
  }, []);

  // Apply theme changes
  const setTheme = (newTheme: 'dark' | 'light') => {
    console.log('🎨 [SET] Setting theme to:', newTheme);
    setThemeState(newTheme);
  };

  // Toggle between dark and light
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    console.log('🌓 [TOGGLE] Clicked! Current:', theme, '→ New:', newTheme);
    
    // CRITICAL: Only toggle 'dark' class for Tailwind compatibility
    document.documentElement.classList.remove('dark');
    document.body.classList.remove('dark');
    
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
    }
    
    document.documentElement.setAttribute('data-theme', newTheme);
    
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
    
    console.log('✅ [TOGGLE] Applied immediately. HTML class:', document.documentElement.className);
    console.log('✅ [TOGGLE] Body class:', document.body.className);
    console.log('✅ [TOGGLE] Has dark class:', document.documentElement.classList.contains('dark'));
    console.log('✅ [TOGGLE] data-theme:', document.documentElement.getAttribute('data-theme'));
    
    // Debug: Log computed styles
    const htmlStyle = window.getComputedStyle(document.documentElement);
    const bodyStyle = window.getComputedStyle(document.body);
    console.log('🔍 [TOGGLE] HTML background-color:', htmlStyle.backgroundColor);
    console.log('🔍 [TOGGLE] Body background-color:', bodyStyle.backgroundColor);
  };

  // CRITICAL: This runs EVERY time theme state changes
  useEffect(() => {
    if (!isInitialized) {
      console.log('⏳ Waiting for initialization...');
      return;
    }
    
    console.log('🎨 [EFFECT] Theme state changed to:', theme);
    console.log('🎨 [EFFECT] Current HTML classes:', document.documentElement.className);
    
    // Verify classes are already correct (from toggle function)
    const hasDarkClass = document.documentElement.classList.contains('dark');
    const shouldHaveDarkClass = theme === 'dark';
    
    if (hasDarkClass === shouldHaveDarkClass) {
      console.log('✅ [EFFECT] Theme already applied correctly, just updating localStorage');
      localStorage.setItem('theme', theme);
      return;
    }
    
    // Remove dark class and re-add if needed
    document.documentElement.classList.remove('dark');
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    }
    document.documentElement.setAttribute('data-theme', theme);
    
    // Persist
    localStorage.setItem('theme', theme);
    
    // Verify
    console.log('✅ [EFFECT] Applied! HTML has "dark":', document.documentElement.classList.contains('dark'));
    console.log('✅ [EFFECT] localStorage:', localStorage.getItem('theme'));
    
    // Force reflow to ensure styles update
    void document.documentElement.offsetHeight;
    
  }, [theme, isInitialized]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
