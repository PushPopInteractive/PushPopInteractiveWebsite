import test from 'node:test';
import assert from 'node:assert/strict';
import {latestInstallHref, refreshInstallLink, enableLatestInstalls} from '../tools/latest-install.mjs';
const manifest='https://github.com/PushPopInteractive/PushPopInteractiveWebsite/releases/download/install-fireside/manifest.plist';
const target=href=>new URL(new URL(href).searchParams.get('url'));
test('nested manifest query remains fully inside the itms URL parameter',()=>{
 const href=latestInstallHref(manifest+'?build=49','tap-one');
 assert.equal(new URL(href).searchParams.get('action'),'download-manifest');
 assert.equal(target(href).searchParams.get('install'),'tap-one');
 assert.equal(target(href).searchParams.get('build'),'49');
 assert.equal(new URL(href).searchParams.size,2);
});
test('a cached page reuses the permanent latest manifest, never a numbered package',()=>{
 const row={dataset:{installManifest:manifest},href:'itms-services://?action=download-manifest&url=OLD-46'};
 refreshInstallLink(row,'new-tap');assert.equal(target(row.href).pathname,new URL(manifest).pathname);
 assert.ok(!row.href.includes('46'));assert.equal(target(row.href).searchParams.get('install'),'new-tap');
});
test('every click refreshes synchronously without cancelling the navigation',()=>{
 let click; const row={dataset:{installManifest:manifest},addEventListener(type,fn){assert.equal(type,'click');click=fn}};
 enableLatestInstalls({querySelectorAll(selector){assert.equal(selector,'[data-latest-install]');return[row]}});
 const first=row.href; click();const second=row.href;click();
 assert.notEqual(first,second);assert.notEqual(second,row.href);
 assert.equal(target(row.href).pathname,new URL(manifest).pathname);
});
test('reject insecure install manifests',()=>assert.throws(()=>latestInstallHref('http://example.org/app.plist','x'),/HTTPS/));
