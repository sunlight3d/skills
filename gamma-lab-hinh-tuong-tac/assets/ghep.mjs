#!/usr/bin/env node
/**
 * ghep.mjs — Công cụ ghép trang hình tương tác Gamma Lab thành file HTML độc lập.
 * Tự động nhúng trực tiếp the.css và iso-kit.js vào HTML để chạy độc lập không phụ thuộc file ngoài.
 *
 * Cách dùng:
 *   node assets/ghep.mjs index.html -o bundle.html
 *   node assets/ghep.mjs --new my-model.html
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const THE_CSS_PATH = resolve(__dirname, 'the.css');
const ISO_KIT_PATH = resolve(__dirname, 'iso-kit.js');

const cssContent = existsSync(THE_CSS_PATH) ? readFileSync(THE_CSS_PATH, 'utf-8') : '';
const jsContent = existsSync(ISO_KIT_PATH) ? readFileSync(ISO_KIT_PATH, 'utf-8') : '';

const args = process.argv.slice(2);

if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
  console.log(`
Cách sử dụng:
  node ghep.mjs <input.html> [-o <output.html>]
  node ghep.mjs --new <output.html> [tên mô hình]

Tùy chọn:
  --new, -n    Tạo một file mẫu HTML hình tương tác mới chuẩn Gamma Lab
  -o, --out    Đường dẫn file xuất ra (mặc định ghi đè hoặc in ra stdout)
  -h, --help   Xem hướng dẫn
`);
  process.exit(0);
}

if (args[0] === '--new' || args[0] === '-n') {
  const outFile = args[1] || 'mo-hinh-tuong-tac.html';
  const title = args[2] || 'Mô hình Tương tác Isometric';
  const template = `<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title} · Gamma Lab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Dela+Gothic+One&display=swap" rel="stylesheet">
<style>
${cssContent}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <div class="eyebrow">Gamma Lab · Hình tương tác</div>
      <h1>${title}</h1>
    </div>
    <p class="lead">Mô hình giải thích nguyên lý hoạt động bằng hình chiếu trục đo (Isometric 3D) tương tác.</p>
  </header>

  <div class="stage">
    <div class="card fig">
      <div class="figbar">
        <span><span class="fign">Hình 1</span> · Toàn cảnh</span>
        <span>Góc nhìn 45°</span>
      </div>
      <svg id="iso" viewBox="0 0 680 440" role="img" aria-label="${title}"></svg>
      <div class="figbar">
        <span>Gợi ý: Nhấn bộ phận · Kéo thanh trượt</span>
        <span><b>Sẵn sàng</b></span>
      </div>
    </div>

    <div class="panel card">
      <div class="ctl">
        <div class="row">
          <label for="p1">Tham số 1</label>
          <output id="v1">50</output>
        </div>
        <input type="range" id="p1" min="0" max="100" value="50">
      </div>

      <div class="btns">
        <button id="btn-apart">Tháo rời</button>
        <button id="btn-sound">Âm thanh: Bật</button>
      </div>

      <div class="read">
        <div class="tile">
          <div class="k">Chỉ số A</div>
          <div class="v" id="stat-a">100</div>
        </div>
        <div class="tile">
          <div class="k">Chỉ số B</div>
          <div class="v" id="stat-b">50%</div>
        </div>
      </div>

      <div class="verdict" id="verdict">Hệ thống đang hoạt động ổn định ở định mức tiêu chuẩn.</div>
    </div>
  </div>

  <div class="card note">
    <div class="n" id="note-n">1</div>
    <div>
      <h2 id="note-title">Bộ phận chính</h2>
      <p id="note-desc">Nhấn vào từng bộ phận trên mô hình để xem thuyết minh chi tiết.</p>
      <div class="parts" id="parts-legend"></div>
    </div>
  </div>
</div>

<script>
${jsContent}
</script>
<script>
(function() {
  const { create, figure, bindRange } = IsoKit;
  const svg = document.getElementById('iso');
  const ctx = create(svg, { ox: 340, oy: 220, scale: 1 });

  // Định nghĩa các bộ phận
  const parts = [
    {
      id: 'base',
      n: 1,
      h: 'Khung đế',
      p: 'Đế chịu lực gia công từ hợp kim đúc, nâng đỡ toàn bộ cơ cấu.',
      draw(g, c) {
        c.slab(g, -120, -80, 0, 240, 160, 15, '#c9c5bb', { halo: true });
      },
      pin: [0, 0, 15],
      apart: [0, 0, -30],
      depth: 0
    },
    {
      id: 'core',
      n: 2,
      h: 'Trụ xử lý',
      p: 'Khoang xử lý trung tâm với van điều áp và cảm biến nhiệt độ.',
      draw(g, c) {
        c.cyl(g, 0, 0, 15, 45, 90, '#7F0220', { bands: [40, 70] });
      },
      pin: [0, 0, 105],
      apart: [0, 0, 40],
      depth: 1
    }
  ];

  const fig = figure(ctx, parts, { selected: 'core' });
  fig.legend(document.getElementById('parts-legend'));

  fig.on('select', part => {
    document.getElementById('note-n').textContent = part.n;
    document.getElementById('note-title').textContent = part.h;
    document.getElementById('note-desc').textContent = part.p;
  });

  document.getElementById('btn-apart').addEventListener('click', () => {
    const isApart = !fig.apart;
    fig.setApart(isApart);
    document.getElementById('btn-apart').textContent = isApart ? 'Ráp lại' : 'Tháo rời';
  });
})();
</script>
</body>
</html>
`;
  writeFileSync(outFile, template, 'utf-8');
  console.log(`Đã tạo file mẫu thành công: ${outFile}`);
  process.exit(0);
}

// Chế độ gộp (bundle)
const inputFile = args[0];
let outIndex = args.indexOf('-o');
if (outIndex === -1) outIndex = args.indexOf('--out');
const outputFile = outIndex !== -1 ? args[outIndex + 1] : inputFile;

if (!existsSync(inputFile)) {
  console.error(`Lỗi: Không tìm thấy file đầu vào: ${inputFile}`);
  process.exit(1);
}

let html = readFileSync(inputFile, 'utf-8');

// Thay thế link the.css hoặc chèn the.css
if (html.includes('<link rel="stylesheet" href="the.css">') || html.includes("<link rel='stylesheet' href='the.css'>")) {
  html = html.replace(/<link rel=["']stylesheet["'] href=["'].*?the\.css["']>(\r?\n)?/, `<style>\n${cssContent}\n</style>\n`);
} else if (!html.includes(cssContent.slice(0, 50))) {
  html = html.replace('</head>', `<style>\n${cssContent}\n</style>\n</head>`);
}

// Thay thế script iso-kit.js hoặc chèn iso-kit.js
if (html.includes('<script src="iso-kit.js"></script>') || html.includes("<script src='iso-kit.js'></script>")) {
  html = html.replace(/<script src=["'].*?iso-kit\.js["']><\/script>(\r?\n)?/, `<script>\n${jsContent}\n</script>\n`);
} else if (!html.includes('IsoKit = { create, figure')) {
  html = html.replace('</body>', `<script>\n${jsContent}\n</script>\n</body>`);
}

writeFileSync(outputFile, html, 'utf-8');
console.log(`Đã ghép hoàn tất: ${outputFile}`);
