/* iso-kit.js — bộ dựng hình isometric tương tác cho Gamma Lab (skill hinh-tuong-tac)
   Không phụ thuộc thư viện. Dán nguyên file này vào <script> của trang (hoặc dùng assets/ghep.mjs).
   Toạ độ mô hình: x đi sang phải-xuống, y đi sang trái-xuống, z đi lên. Đơn vị = px khi scale = 1.
   Quy tắc màu: mỗi bộ phận MỘT màu gốc, kit tự ra 4 tông (đỉnh sáng, mặt phải, mặt trái tối, bóng dưới).
*/
(function (global) {
  const NS = 'http://www.w3.org/2000/svg';
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const hex = h => { const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(h); return m ? m.slice(1).map(s => parseInt(s, 16)) : [128, 128, 128]; };
  const toHex = c => '#' + c.map(v => clamp(Math.round(v), 0, 255).toString(16).padStart(2, '0')).join('');
  const shade = (col, k) => toHex(hex(col).map(v => v * k));          // k<1 tối, k>1 sáng
  const mix = (a, b, t) => { const A = hex(a), B = hex(b); return toHex(A.map((v, i) => v + (B[i] - v) * t)); };
  const tones = col => ({ top: shade(col, 1.10), right: shade(col, 0.90), left: shade(col, 0.72), lo: shade(col, 0.55) });
  const fmt = (n, d = 1) => Number(n).toFixed(d).replace('.', ',');  // kiểu số Việt: 9,0

  /** Tạo ngữ cảnh vẽ trên một <svg>. opt: {ox, oy, scale, edge, edgeWidth} */
  function create(svg, opt = {}) {
    const ox = opt.ox ?? 320, oy = opt.oy ?? 250, S = opt.scale ?? 1;
    const EDGE = opt.edge || '#2b1b17', EW = opt.edgeWidth ?? 1;
    const iso = (x, y, z) => [ox + (x - y) * 0.866 * S, oy + (x + y) * 0.5 * S - z * S];
    const el = (n, a = {}, par) => { const e = document.createElementNS(NS, n); for (const k in a) if (a[k] != null) e.setAttribute(k, a[k]); (par || svg).appendChild(e); return e; };
    const pts = arr => arr.map(p => p.map(v => +v.toFixed(2)).join(',')).join(' ');
    const E = { stroke: EDGE, 'stroke-width': EW, 'stroke-linejoin': 'round', class: 'edge' };
    const poly = (p, fill, par, extra) => el('polygon', Object.assign({ points: pts(p), fill }, E, extra || {}), par);
    let defs = svg.querySelector('defs') || el('defs');
    const grads = {};
    /** gradient ngang cho trụ: tối ở mép trái, sáng gần giữa-phải (ánh sáng từ trên-phải) */
    function cylGrad(col) {
      if (grads[col]) return grads[col];
      const id = 'cg' + Object.keys(grads).length + '_' + col.slice(1);
      const g = el('linearGradient', { id, x1: 0, x2: 1, y1: 0, y2: 0 }, defs);
      [[0, 0.62], [0.35, 0.92], [0.62, 1.02], [1, 0.70]].forEach(([o, k]) => el('stop', { offset: o, 'stop-color': shade(col, k) }, g));
      grads[col] = `url(#${id})`; return grads[col];
    }

    /** bóng mờ dưới chân một bộ phận (đổ lên mặt đang đỡ nó) */
    function halo(g, x, y, z, rx, ry, k = 0.14) {
      const [cx, cy] = iso(x, y, z); return el('ellipse', { cx, cy: cy + 1, rx, ry, fill: 'rgba(0,0,0,' + k + ')', class: 'halo' }, g);
    }

    /** hộp: gốc (x,y,z), kích thước w (theo x), d (theo y), h (lên). o: {halo:true (bóng dưới chân, chỉ cho bộ phận đứng trên sàn), seam, screws} */
    function box(g, x, y, z, w, d, h, col, o = {}) {
      const T = tones(col);
      if (o.halo) halo(g, x + w / 2, y + d / 2, z, (w + d) * 0.5, (w + d) * 0.26);   // chỉ bật halo cho bộ phận đứng trên sàn
      const top = [iso(x, y, z + h), iso(x + w, y, z + h), iso(x + w, y + d, z + h), iso(x, y + d, z + h)];
      const right = [iso(x + w, y, z), iso(x + w, y + d, z), iso(x + w, y + d, z + h), iso(x + w, y, z + h)];
      const left = [iso(x, y + d, z), iso(x + w, y + d, z), iso(x + w, y + d, z + h), iso(x, y + d, z + h)];
      const fL = poly(left, T.left, g), fR = poly(right, T.right, g), fT = poly(top, T.top, g);
      if (o.screws) [[x + 4, y + 4], [x + w - 4, y + 4], [x + w - 4, y + d - 4], [x + 4, y + d - 4]].forEach(([sx, sy]) => { const [cx, cy] = iso(sx, sy, z + h); el('circle', { cx, cy, r: 1.4, fill: T.lo }, g); });
      if (o.seam) { // một đường gân chạy quanh thân, cao o.seam từ đáy, chạy hết mép (không hụt góc)
        const s = z + o.seam; el('polyline', { points: pts([iso(x, y + d, s), iso(x + w, y + d, s), iso(x + w, y, s)]), fill: 'none', stroke: T.lo, 'stroke-width': EW, opacity: .7 }, g);
      }
      return { top: fT, right: fR, left: fL, tones: T };
    }

    /** tấm phẳng mỏng (sàn, khay): như box nhưng không halo */
    const slab = (g, x, y, z, w, d, h, col, o = {}) => box(g, x, y, z, w, d, h, col, Object.assign({ halo: false }, o));

    /** trụ đứng tâm (x,y) đáy z, bán kính r, cao h. o: {bands:[z1,z2], halo:true, flat:true (không gradient)} */
    function cyl(g, x, y, z, r, h, col, o = {}) {
      const rx = r * 0.866 * 1.15, ry = r * 0.5 * 1.15;
      const [cx, cy] = iso(x, y, z), [tx, ty] = iso(x, y, z + h);
      if (o.halo) halo(g, x, y, z, rx * 1.15, ry * 1.15);
      const body = el('path', { d: `M${cx - rx},${cy} L${tx - rx},${ty} A${rx},${ry} 0 0 0 ${tx + rx},${ty} L${cx + rx},${cy} A${rx},${ry} 0 0 1 ${cx - rx},${cy} Z`, fill: o.flat ? shade(col, .85) : cylGrad(col), stroke: EDGE, 'stroke-width': EW, class: 'edge' }, g);
      (o.bands || []).forEach(bz => { const [bx, by] = iso(x, y, z + bz); el('path', { d: `M${bx - rx},${by} A${rx},${ry} 0 0 0 ${bx + rx},${by}`, fill: 'none', stroke: shade(col, .6), 'stroke-width': EW, opacity: .8 }, g); });
      const top = el('ellipse', { cx: tx, cy: ty, rx, ry, fill: shade(col, 1.1), stroke: EDGE, 'stroke-width': EW, class: 'edge' }, g);
      return { body, top, rx, ry, cx: tx, cy: ty, tones: tones(col) };
    }

    /** ống: đi qua các điểm mô hình, bán kính r. Đầu ống có chấm nối (ống không lơ lửng). o: {dots: true | false | 'start' | 'end'} */
    function tube(g, points, r, col, o = {}) {
      const P = points.map(p => iso(...p)); const d = 'M' + P.map(p => p.map(v => v.toFixed(1)).join(',')).join(' L');
      const base = { d, fill: 'none', 'stroke-linejoin': 'round', 'stroke-linecap': 'round' };
      el('path', Object.assign({}, base, { stroke: EDGE, 'stroke-width': r * 2 + EW * 2 }), g);
      const body = el('path', Object.assign({}, base, { stroke: shade(col, .85), 'stroke-width': r * 2 }), g);
      const hi = el('path', Object.assign({}, base, { stroke: shade(col, 1.25), 'stroke-width': Math.max(1, r * .5), opacity: .7 }), g);
      const ends = o.dots === false ? [] : o.dots === 'start' ? [P[0]] : o.dots === 'end' ? [P[P.length - 1]] : [P[0], P[P.length - 1]];
      ends.forEach(([cx, cy]) => el('circle', { cx, cy, r: r * 1.5, fill: shade(col, .7), stroke: EDGE, 'stroke-width': EW }, g));
      return { d, body, hi, P };
    }

    /** nhãn số (balloon) tại điểm mô hình, kèm thẻ chữ bên phải nếu có tag (tên + số sống, cập nhật bằng figure.setTag).
     *  Người dùng Gamma Lab muốn đọc được "ô này là gì, đang bao nhiêu" ngay trong hình. */
    function pin(g, x, y, z, n, col = '#7F0220', tag, opt = {}) {
      const [cx, cy] = iso(x, y, z); const t = el('g', { class: 'pin' + (opt.apartOnly ? ' apart-only' : '') }, g); let bg = null, txt = null;
      if (tag) {
        bg = el('rect', { x: cx + 12, y: cy - 8.5, width: 40, height: 17, rx: 8.5, fill: '#FFFDF7', stroke: '#2b1b17', 'stroke-width': .8, opacity: .96 }, t);
        txt = el('text', { x: cx + 19, y: cy + 3.6, fill: '#2b1b17', 'font-size': 10, 'font-weight': 600, 'font-family': 'Be Vietnam Pro, sans-serif' }, t); txt.textContent = tag;
      }
      el('circle', { cx, cy, r: 11, fill: col, stroke: '#F6EAD0', 'stroke-width': 1.5 }, t);
      el('text', { x: cx, y: cy + 4.2, 'text-anchor': 'middle', fill: '#F6EAD0', 'font-size': 12, 'font-family': 'Dela Gothic One, sans-serif' }, t).textContent = n;
      const fit = () => { if (txt) bg.setAttribute('width', (txt.getComputedTextLength() + 14).toFixed(1)); };
      fit();
      return { g: t, txt, bg, set(s) { if (txt) { txt.textContent = s; fit(); } }, fit };
    }

    /** lưới ô vuông trên một mặt phẳng (khay thoát nước, sàn) */
    function grid(g, x, y, z, w, d, step, col) {
      for (let i = step; i < w; i += step) el('line', { x1: iso(x + i, y, z)[0], y1: iso(x + i, y, z)[1], x2: iso(x + i, y + d, z)[0], y2: iso(x + i, y + d, z)[1], stroke: col, 'stroke-width': .6, opacity: .7 }, g);
      for (let j = step; j < d; j += step) el('line', { x1: iso(x, y + j, z)[0], y1: iso(x, y + j, z)[1], x2: iso(x + w, y + j, z)[0], y2: iso(x + w, y + j, z)[1], stroke: col, 'stroke-width': .6, opacity: .7 }, g);
    }

    /** chữ nhỏ khắc trên mặt (tối đa một nhãn/hình, theo nguyên tắc Anatomy) */
    function engrave(g, x, y, z, text, col = '#2b1b17', size = 9) {
      const [cx, cy] = iso(x, y, z); return el('text', { x: cx, y: cy, 'text-anchor': 'middle', fill: col, 'font-size': size, 'font-family': 'Be Vietnam Pro, sans-serif', 'font-weight': 600, opacity: .8 }, g);
    }

    return { svg, iso, el, poly, box, slab, cyl, tube, pin, halo, grid, engrave, shade, mix, tones, EDGE, EW, S, defs };
  }

  /** Hình = tập bộ phận. parts: [{id, n, h, p, tag, draw(g, ctx), pin:[x,y,z], apart:[dx,dy,dz], depth}]
   *  - tag: chữ ngắn hiện cạnh nhãn số ("Nồi hơi 93 °C"); đổi lúc chạy bằng fig.setTag(id, text).
   *  - pinApartOnly: true cho bộ phận bị bao bên trong (nhãn chỉ hiện khi tháo rời).
   *  - depth: số càng nhỏ vẽ càng trước (xa). Mặc định theo thứ tự khai báo.
   *  - draw() vẽ vào <g> riêng; pin đặt nhãn số; apart là độ dời khi tháo rời.
   *  Trả về {groups, select, setApart, on, parts}
   */
  function figure(ctx, parts, opt = {}) {
    const groups = {}, pins = {}; const listeners = { select: [] }; let sel = opt.selected || parts[0].id; let apart = false;
    const ordered = parts.map((p, i) => Object.assign({ _i: i }, p)).sort((a, b) => (a.depth ?? a._i) - (b.depth ?? b._i));
    ordered.forEach((pt, k) => {
      const g = ctx.el('g', { class: 'p', id: 'g-' + pt.id, tabindex: 0, role: 'button', 'aria-label': pt.h });
      g.style.transitionDelay = (k * 35) + 'ms';
      pt.draw(g, ctx); groups[pt.id] = g;
      if (pt.pin) pins[pt.id] = ctx.pin(g, ...pt.pin, pt.n, undefined, pt.tag, { apartOnly: !!pt.pinApartOnly });   // pinApartOnly: bộ phận nằm trong, nhãn chỉ hiện khi tháo rời
      g.addEventListener('click', () => select(pt.id));
      g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(pt.id); } });
    });
    function select(id) { sel = id; parts.forEach(p => groups[p.id].classList.toggle('sel', p.id === id)); listeners.select.forEach(f => f(parts.find(p => p.id === id))); }
    function setApart(v) {
      apart = v; parts.forEach(p => { const g = groups[p.id]; const a = apart && p.apart ? p.apart : [0, 0, 0]; const k = opt.apartScale ?? 0.9;
        const x = (a[0] - a[1]) * 0.866 * k, y = (a[0] + a[1]) * 0.5 * k - a[2] * k; g.style.transform = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px)`; });
      ctx.svg.classList.toggle('apart', apart);
    }
    const on = (ev, f) => listeners[ev].push(f);
    const setTag = (id, text) => { if (pins[id]) pins[id].set(text); };
    const refreshTags = () => Object.values(pins).forEach(p => p.fit());
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refreshTags);   // font tải xong thì đo lại bề rộng thẻ
    /** tạo nút chọn bộ phận (legend) vào một phần tử HTML */
    function legend(container) {
      parts.forEach(pt => { const b = document.createElement('button'); b.type = 'button'; b.textContent = pt.n + '. ' + pt.h.split(' (')[0]; b.id = 'pb-' + pt.id; b.addEventListener('click', () => select(pt.id)); container.appendChild(b); });
      on('select', pt => parts.forEach(p => document.getElementById('pb-' + p.id).setAttribute('aria-pressed', p.id === pt.id)));
    }
    return { groups, pins, select, setApart, on, legend, setTag, refreshTags, parts, get selected() { return sel; }, get apart() { return apart; } };
  }

  /** gắn nhiều thanh trượt vào một hàm update; trả về hàm đọc giá trị */
  function bindRange(ids, update) {
    const read = () => Object.fromEntries(ids.map(id => [id, +document.getElementById(id).value]));
    ids.forEach(id => document.getElementById(id).addEventListener('input', () => update(read())));
    return read;
  }

  global.IsoKit = { create, figure, bindRange, shade, mix, tones, fmt, clamp };
})(window);
