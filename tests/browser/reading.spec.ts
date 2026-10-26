import {test,expect} from '@playwright/test';
test('home and category navigation work on desktop and mobile',async({page},testInfo)=>{
 await page.goto('/');
 await expect(page.getByRole('heading',{level:1})).toContainText('读懂供应链');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
 await page.screenshot({path:testInfo.outputPath('home.png'),fullPage:true});
 await page.getByRole('link',{name:/开始阅读/}).click();
 await expect(page.locator('.category-card')).toHaveCount(7);
 await page.locator('.category-card').first().click();
 await expect(page).toHaveURL(/categories\/foundations/);
});
test('lookup works in Chinese and keeps ambiguous meanings',async({page})=>{
 await page.goto('/vocabulary/');await page.getByRole('textbox').fill('可承诺量');
 await expect(page.locator('#results .result').first()).toContainText('ATP');
 await page.locator('#results .result').first().click();await expect(page).toHaveURL(/s104/);
 await expect(page.locator('article h1')).toHaveText('ATP');await expect(page.locator('table').first()).toContainText('Available to Promise');
 await page.goto('/vocabulary/');await page.getByRole('textbox').fill('ABC');
 await expect(page.locator('#results .result').filter({hasText:'ABC分类分析'})).toBeVisible();
 await expect(page.locator('#results .result').filter({hasText:'活动成本法'}).first()).toBeVisible();
});
test('reader tables stay inside the mobile viewport',async({page},testInfo)=>{
 await page.goto('/articles/s002/');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
 await expect(page.locator('article section').first()).toBeVisible();
 await expect(page.locator('.table-scroll').first()).toBeVisible();
 await page.screenshot({path:testInfo.outputPath('reader.png'),fullPage:true});
});
test('both complete downloads are available',async({page,request})=>{
 await page.goto('/downloads/');
 for(const ext of ['pdf','epub']){const r=await request.get(`/downloads/supasara-complete.${ext}`);expect(r.ok()).toBeTruthy();expect((await r.body()).length).toBeGreaterThan(10000);}
 await expect(page.getByRole('link',{name:/下载 PDF/})).toBeVisible();await expect(page.getByRole('link',{name:/下载 EPUB/})).toBeVisible();
});
