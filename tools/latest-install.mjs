// Keep the user gesture synchronous: iOS receives a freshly addressed manifest
// on the original tap, without waiting for a fetch or opening an intermediate page.
let tap = 0;
export function latestInstallHref(manifest, nonce) {
  const url = new URL(manifest);
  if (url.protocol !== 'https:') throw new Error('Install manifests require HTTPS');
  url.searchParams.set('install', nonce);
  return 'itms-services://?action=download-manifest&url=' + encodeURIComponent(url.href);
}
export function refreshInstallLink(row, nonce = `${Date.now()}-${++tap}`) {
  row.href = latestInstallHref(row.dataset.installManifest, nonce);
}
export function enableLatestInstalls(root) {
  for (const row of root.querySelectorAll('[data-latest-install]')) {
    refreshInstallLink(row);
    row.addEventListener('click', () => refreshInstallLink(row));
  }
}
if (typeof document !== 'undefined') {
  enableLatestInstalls(document);
  window.addEventListener('pageshow', () => {
    for (const row of document.querySelectorAll('[data-latest-install]')) refreshInstallLink(row);
  });
}
