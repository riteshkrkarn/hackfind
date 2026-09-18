import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(__dirname, "../public/textures");
const outPng = path.join(outDir, "badge-matte.png");
const outMeta = path.join(outDir, "badge-matte.png.json");

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 512, height: 512 } });
  await page.setContent(`<!doctype html>
<html><body style="margin:0">
<canvas id="c" width="512" height="512"></canvas>
<script>
  const c = document.getElementById("c");
  const ctx = c.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 512, 512);
  g.addColorStop(0, "#eef1ec");
  g.addColorStop(0.45, "#e4e8e1");
  g.addColorStop(1, "#d6dbd2");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 512, 512);
  const img = ctx.getImageData(0, 0, 512, 512);
  for (let i = 0; i < img.data.length; i += 4) {
    const n = Math.random() * 28 - 14;
    img.data[i] = Math.max(0, Math.min(255, img.data[i] + n));
    img.data[i + 1] = Math.max(0, Math.min(255, img.data[i + 1] + n * 0.95));
    img.data[i + 2] = Math.max(0, Math.min(255, img.data[i + 2] + n * 0.85));
  }
  ctx.putImageData(img, 0, 0);
</script>
</body></html>`);
  await page.waitForTimeout(120);
  await page.locator("#c").screenshot({ path: outPng });
  fs.writeFileSync(
    outMeta,
    JSON.stringify(
      {
        prompt:
          "Procedural matte badge stock: cool paper gradient #eef1ec to #d6dbd2 with fine fiber noise for Hackfind check-in rail badges",
        origin: "generated-local-canvas",
        createdAt: new Date().toISOString(),
      },
      null,
      2,
    ),
  );
  await browser.close();
  console.log("texture ok", outPng);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
