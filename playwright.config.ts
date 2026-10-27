import {defineConfig,devices} from '@playwright/test';
const baseURL=`http://127.0.0.1:${process.env.PORT||3177}`;

export default defineConfig({
 testDir:'./tests/browser',
 use:{baseURL},
 webServer:{
  command:'node scripts/preview.mjs',
  url:baseURL,
  reuseExistingServer:false,
 },
 projects:[
  {name:'desktop',use:{...devices['Desktop Chrome']}},
  {name:'mobile',use:{...devices['iPhone 13']}},
 ],
});
