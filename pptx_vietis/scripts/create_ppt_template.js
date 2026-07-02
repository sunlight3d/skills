const pptxgen = require("pptxgenjs");
const path = require("path");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9'; 
pres.author = 'VietIS';
pres.title = 'VietIS Presentation';

// --- VIETIS BRAND COLORS ---
const TEAL = "00A89D";
const ORANGE = "F05A28";
const LIGHT_TEAL = "E6F6F5";
const LIGHT_ORANGE = "FDEEE9";
const DARK_GRAY = "333333";

// --- ASSETS ---
// Use __dirname so it correctly points to the assets folder regardless of execution path
const logoPath = path.join(__dirname, '..', 'assets', 'logo.png');
const genBgPath = path.join(__dirname, '..', 'assets', 'bg.png');

// --- DEFINE SLIDE MASTER ---
pres.defineSlideMaster({
  title: 'MASTER_SLIDE',
  background: { path: genBgPath },
  objects: [
    { image: { x: 0.5, y: 0.25, w: 1.5, h: 0.53, path: logoPath } }
  ]
});

// --- HELPER FUNCTIONS ---
function addTitle(slide, text, color = TEAL) {
  slide.addText(text, { x: 0.5, y: 1.0, w: 9, h: 0.6, fontSize: 26, bold: true, color: color, fontFace: 'Arial' });
}

function addSubtext(slide, text) {
  slide.addText(text, { x: 0.5, y: 1.6, w: 9, h: 0.4, fontSize: 16, color: DARK_GRAY, fontFace: 'Arial' });
}

function addBox(slide, x, y, w, h, symbol, title, body, bgColor, borderColor, titleColor) {
  let textItems = [];
  if (symbol) {
    // 1 space spacing, slightly smaller size (22) for baseline alignment
    textItems.push({ text: symbol + " ", options: { fontSize: 22, fontFace: 'Segoe UI Emoji', color: titleColor } });
  }
  
  if (title) {
    // paraSpaceAfter: 4 controls the gap between title and body natively without inserting a blank line
    textItems.push({ text: title, options: { fontSize: 18, bold: true, color: titleColor, fontFace: 'Arial', breakLine: true, paraSpaceAfter: 4 } });
  }
  
  if (body) {
    textItems.push({ text: body, options: { fontSize: 14, color: DARK_GRAY, fontFace: 'Arial', lineSpacingMultiple: 1.2 } });
  }

  slide.addText(textItems, {
    x: x, y: y, w: w, h: h,
    shape: pres.shapes.ROUNDED_RECTANGLE,
    fill: { color: bgColor },
    line: { color: borderColor, width: 1 }, 
    rectRadius: 0.1,
    margin: 10, // Must be 10 so text doesn't overflow
    valign: 'middle',
    align: 'center'
  });
}

function addArrow(slide, x, y, w, h, dir) {
  const shape = dir === 'down' ? pres.shapes.DOWN_ARROW : pres.shapes.RIGHT_ARROW;
  slide.addShape(shape, {
    x: x, y: y, w: w, h: h,
    fill: { color: "CCCCCC" },
    line: { color: "AAAAAA", width: 1 } 
  });
}

// ---------------------------------------------------------
// Example Slide Generation
let slide1 = pres.addSlide({ masterName: "MASTER_SLIDE" });
addTitle(slide1, "TIÊU ĐỀ SLIDE", TEAL);
addSubtext(slide1, "Dòng mô tả phụ dưới tiêu đề.");
addBox(slide1, 0.5, 2.5, 4.0, 1.5, "🚀", "Tốc độ triển khai", "Sử dụng template để làm slide nhanh gấp nhiều lần.", LIGHT_TEAL, TEAL, TEAL);
addArrow(slide1, 4.7, 3.0, 0.4, 0.4, 'right');
addBox(slide1, 5.3, 2.5, 4.0, 1.5, "🎨", "Đồng bộ thương hiệu", "Luôn chuẩn màu sắc và kích thước theo VietIS Brand Guidelines.", LIGHT_ORANGE, ORANGE, ORANGE);

// Save the PPTX
pres.writeFile({ fileName: "VietIS_Presentation_Generated.pptx" })
  .then(() => {
    console.log("PPTX created successfully!");
  })
  .catch(err => {
    console.error(err);
  });
