/* Branding and shared presentation only. Backend/data contracts are unchanged. */
(() => {
  const brand=window.LUMA_BRAND;
  document.title=brand.title;
  document.querySelectorAll('[data-brand-name]').forEach(el=>el.textContent=brand.name);
  const mark='<svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M8 7v18h17" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="21" cy="10" r="4" fill="currentColor"/></svg>';
  document.querySelectorAll('[data-brand-mark]').forEach(el=>el.innerHTML=mark);
  const paths={chance:'M12 3 15 9 21 12 15 15 12 21 9 15 3 12 9 9Z',luck:'M3 17 9 11 13 14 21 5 M15 5h6v6',listen:'M5 13V9a7 7 0 0 1 14 0v4 M5 11H3v7h4v-7H5 M19 11h2v7h-4v-7h2 M17 18v2h-5',question:'M4 4h16v12H9l-5 4V4 M8 8h8 M8 12h5'};
  document.querySelectorAll('[data-question-mode]').forEach(el=>{
    const text=el.textContent.trim().replace(/^[^\s]+\s+/,'');
    el.innerHTML='<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="'+paths[el.dataset.questionMode]+'"/></svg><span>'+text+'</span>';
  });
  // Keep a readable name when the compact settings control only displays its dot.
  document.querySelectorAll('.api-trigger').forEach(el=>{el.setAttribute('aria-label','分析服务设置');el.title='分析服务设置';});
})();
