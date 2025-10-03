Target performance and bundle size budgets (student project)
API performance (dev-grade)
P50 < 200 ms, P95 < 800 ms for simple GETs (local/Basic tier)
Cold start first request can be slower; subsequent should meet above
Throughput
Single instance App Service; ok for classroom/demo traffic
Frontend bundle budgets (CRA build)
Main JS (initial): ≤ 300 KB gzipped
Total JS loaded at startup (initial): ≤ 500 KB gzipped
CSS: ≤ 100 KB gzipped
Images: optimized; single image ≤ 300 KB (prefer WebP)
Web vitals (manual target)
LCP < 2.5s, CLS < 0.1, TBT < 300ms on a basic laptop network
Build-time checks
npm run build prints asset sizes; warn if any single gzipped JS chunk > 300 KB
Optional: use source-map-explorer or webpack-bundle-analyzer for any spike
Monitoring (lightweight)
Enable App Service logs; keep simple curl checks in CI
Manual Lighthouse run on the dashboard page before release