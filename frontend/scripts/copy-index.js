const fs = require('fs')
const path = require('path')

const outDir = path.resolve(__dirname, '..', '..', 'static')
const indexSrc = path.join(outDir, 'index.html')
const templatesDest = path.resolve(__dirname, '..', '..', 'templates', 'index.html')

if (!fs.existsSync(indexSrc)){
  console.error('Built index not found:', indexSrc)
  process.exit(1)
}

const html = fs.readFileSync(indexSrc, 'utf8')
fs.writeFileSync(templatesDest, html)
console.log('Copied built index to', templatesDest)
