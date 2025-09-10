const fs = require('fs')
const path = require('path')

const outDir = path.resolve(__dirname, '..', '..', 'static')
const indexSrc = path.join(outDir, 'index.html')
// Write the built index into backend/static so the backend image serves the SPA
const templatesDest = path.resolve(__dirname, '..', '..', 'backend', 'static', 'index.html')

if (!fs.existsSync(indexSrc)){
  console.error('Built index not found:', indexSrc)
  process.exit(1)
}

// Ensure destination directory exists
const destDir = path.dirname(templatesDest)
if (!fs.existsSync(destDir)){
  fs.mkdirSync(destDir, { recursive: true })
}

const html = fs.readFileSync(indexSrc, 'utf8')
fs.writeFileSync(templatesDest, html)
console.log('Copied built index to', templatesDest)
