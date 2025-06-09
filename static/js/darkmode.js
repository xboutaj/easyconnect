// static/js/darkmode.js

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('dark-toggle');
  if (!toggleBtn) return;

  const updateIcon = () => {
    if (document.documentElement.classList.contains('dark-mode')) {
      toggleBtn.textContent = '☀️';
    } else {
      toggleBtn.textContent = '🌙';
    }
  };

  if (localStorage.getItem('darkMode') === 'true') {
    document.documentElement.classList.add('dark-mode');
  }
  updateIcon();

  toggleBtn.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDark);
    updateIcon();
  });
});
