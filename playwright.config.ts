import {defineConfig,devices} from '@playwright/test';

export default defineConfig({
 testDir:'./tests/browser',
 use:{baseURL:'http://127.0.0.1:3177'},
 webServer:{
  command:'node scripts/preview.mjs',
  url:'http://127.0.0.1:3177',
  reuseExistingServer:false,
 },
 projects:[
  {name:'desktop',use:{...devices['Desktop Chrome']}},
  {name:'mobile',use:{...devices['iPhone 13']}},
 ],
});
