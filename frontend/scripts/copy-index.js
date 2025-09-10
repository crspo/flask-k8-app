const fs = require('fs')
const path = require('path')

// Vite may output to backend/static (this repo) or top-level ./static depending on config.
// Prefer backend/static (our current outDir), then fall back to ./static for older setups.
const candidates = [
  path.resolve(__dirname, '..', '..', 'backend', 'static', 'index.html'),
  path.resolve(__dirname, '..', '..', 'static', 'index.html')
]

let indexSrc = null
for (const c of candidates) {
  if (fs.existsSync(c)) {
    indexSrc = c
    break
  }
}

if (!indexSrc) {
  console.error('Built index not found in expected locations:')
  for (const c of candidates) console.error('  -', c)
  process.exit(1)
}

// Write the built index into backend/static so the backend image serves the SPA
const templatesDest = path.resolve(__dirname, '..', '..', 'backend', 'static', 'index.html')

// Ensure destination directory exists
const destDir = path.dirname(templatesDest)
if (!fs.existsSync(destDir)){
  fs.mkdirSync(destDir, { recursive: true })
}

const html = fs.readFileSync(indexSrc, 'utf8')
fs.writeFileSync(templatesDest, html)
console.log('Copied built index from', indexSrc, 'to', templatesDest)
