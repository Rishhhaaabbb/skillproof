/**
 * PWA Icon Generator
 * ------------------
 * Generates all required PWA icon sizes from a single source SVG/PNG.
 *
 * Usage:
 *   node scripts/generate-icons.mjs
 *
 * Requirements:
 *   npm install --save-dev sharp
 *
 * Place your source icon at: public/icons/icon-source.png (512×512 minimum)
 */

import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const sourceFile = path.join(__dirname, '../public/icons/icon-source.png');
const outputDir = path.join(__dirname, '../public/icons');

async function run() {
  if (!fs.existsSync(sourceFile)) {
    console.error(`❌  Source icon not found at: ${sourceFile}`);
    console.error('   Create a 512×512 PNG at that path and re-run.');
    process.exit(1);
  }

  let sharp;
  try {
    sharp = require('sharp');
  } catch {
    console.error('❌  sharp is not installed. Run: npm install --save-dev sharp');
    process.exit(1);
  }

  for (const size of sizes) {
    const outputPath = path.join(outputDir, `icon-${size}x${size}.png`);
    await sharp(sourceFile)
      .resize(size, size, { fit: 'contain', background: { r: 24, g: 24, b: 27, alpha: 1 } })
      .png()
      .toFile(outputPath);
    console.log(`✅  Generated ${size}×${size} → ${outputPath}`);
  }

  console.log('\nAll icons generated. ');
}

run().catch(console.error);
