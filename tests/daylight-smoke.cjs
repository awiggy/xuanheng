// Run against an isolated backend (never a database containing real profiles).
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.LUMA_TEST_URL;
if (!base || process.env.LUMA_ISOLATED_TEST !== '1') throw new Error('Set LUMA_TEST_URL and LUMA_ISOLATED_TEST=1 for a temporary test database.');
(async () => {
  const browser = await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    for(const [name,date] of [['示例档案 A','1990-05-15'],['示例档案 B','1992-08-20']]){
      const response=await page.request.post(base+'/api/chart',{data:{name,calendar:'solar',date,time:'12:00',sex:'男',place:'北京市',longitude:116.4074,latitude:39.9042,timezoneOffset:8,timeMode:'standard',persistHistory:true}});
      assert.equal(response.ok(),true,await response.text());
    }
    await page.goto(base);await page.waitForTimeout(300);
    await page.locator('#home-page [data-select="1"]').click();
    assert.equal(await page.locator('#home-page .module-card.selected').getAttribute('data-index'),'1');
    await page.locator('#home-page .module-card.selected').focus();await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#home-page .module-card.selected').getAttribute('data-index'),'2');
    const box=await page.locator('#home-page .module-card.selected').boundingBox();
    await page.mouse.move(box.x+box.width/2,box.y+140);await page.mouse.down();await page.mouse.move(box.x+box.width/2-150,box.y+140,{steps:12});await page.mouse.up();
    assert.equal(await page.locator('#home-page .module-card.selected').getAttribute('data-index'),'0');
    await page.waitForTimeout(350);await page.locator('#home-page [data-enter="0"]').click();await page.waitForURL('**/#/chart');
    await page.evaluate(()=>location.hash='/profile');await page.locator('[data-record-action="report"]').first().click();
    await page.waitForFunction(()=>document.querySelector('#results').classList.contains('visible') || (document.querySelector('#results').getBoundingClientRect().height>0&&document.querySelector('#pillars').children.length===4));
    await page.waitForTimeout(400);
    assert.equal(await page.locator('#pillars .pillar').count(),4);
    const headerPositions=[];
    for(const route of ['chart','timing','question','tarot','ziwei','affinity','profile']){
      await page.evaluate(r=>location.hash='/'+r,route);await page.waitForTimeout(route==='ziwei'?1000:350);
      const trigger=await page.locator('.site-page.active .system-trigger').boundingBox();
      headerPositions.push([trigger.x,trigger.y,trigger.width,trigger.height]);
      if(route==='tarot'){
        assert.equal(await page.locator('#tarot-draw').isDisabled(),true);
        await page.locator('#tarot-question').fill('我该如何安排接下来一周的学习？');
        await page.locator('#tarot-draw').click();await page.waitForSelector('.tarot-card-shell');
        const cards=page.locator('.tarot-card-shell');
        for(let i=0;i<await cards.count();i++){await cards.nth(i).click();await page.waitForTimeout(120);}
        await page.waitForTimeout(500);
      }
      if(route==='ziwei'){
        await page.waitForSelector('#ziwei-results:not([hidden]), #ziwei-result:not([hidden])',{timeout:15000});
        await page.locator('#ziwei-report-generate').click();
        await page.waitForSelector('#ziwei-report:not([hidden])',{timeout:15000});
      }
      if(route==='affinity') {
        await page.locator('#affinity-generate').click();await page.waitForSelector('#affinity-result:not([hidden])');
        await page.locator('#affinity-generate').hover();await page.waitForTimeout(250);
        assert.equal(await page.locator('#affinity-generate').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(49, 68, 83)','Primary hover must retain dark background and readable text');
      }
      if(route==='question') {await page.locator('#question-history-toggle').click();assert.equal(await page.locator('#question-history-drawer').getAttribute('aria-hidden'),'false');await page.keyboard.press('Escape');assert.equal(await page.locator('#question-history-drawer').getAttribute('aria-hidden'),'true');}
      await page.screenshot({path:'/tmp/luma-rich-'+route+'.png',fullPage:true});
    }
    assert.ok(headerPositions.every(r=>r.every((v,i)=>Math.abs(v-headerPositions[0][i])<1)),JSON.stringify(headerPositions));
    const failures=[];
    for(const width of [320,390,768,1024,1440]){
      await page.setViewportSize({width,height:1000});
      for(const route of ['home','chart','timing','question','tarot','tarot-history','ziwei','affinity','profile','profile-edit','philosophy']){
        await page.evaluate(r=>location.hash='/'+r,route);await page.waitForTimeout(200);
        const check=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,fonts:[...new Set([...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().width&&getComputedStyle(e).visibility!=='hidden').map(e=>getComputedStyle(e).fontFamily))]}));
        if(check.overflow||check.fonts.length!==1)failures.push({width,route,...check});
        if(route==='profile-edit'){
          const modal=await page.locator('.editor-page .editor-main').boundingBox();
          assert.ok(Math.abs(modal.x+modal.width/2-width/2)<1,'Birth editor must be horizontally centered');
          const wheels=await page.locator('#solar-wheel-grid .wheel-scroller').evaluateAll(es=>es.map(e=>({scroll:e.scrollTop,index:[...e.querySelectorAll('.wheel-item')].indexOf(e.querySelector('.selected'))})));
          assert.ok(wheels.every(w=>Math.abs(w.scroll-w.index*34)<1),'Wheel selection must stay aligned with its value');
        }
        if(width===390&&['home','profile-edit','question','ziwei'].includes(route))await page.screenshot({path:'/tmp/luma-mobile-'+route+'.png',fullPage:true});
      }
    }
    console.log(JSON.stringify({errors,failures},null,2));assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
