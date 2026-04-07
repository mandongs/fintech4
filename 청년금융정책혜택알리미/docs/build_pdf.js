const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DOCS_DIR = path.dirname(__filename);
const OUT_HTML = path.join(DOCS_DIR, '_combined.html');
const OUT_PDF  = path.join(DOCS_DIR, '청년금융정책혜택알리미_기획_개발정의서.pdf');
const CHROME   = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

// ── 파일 읽기
const html1 = fs.readFileSync(path.join(DOCS_DIR, '기획정의서.html'), 'utf8');
const html2 = fs.readFileSync(path.join(DOCS_DIR, '개발상세정의서.html'), 'utf8');

// ── <body>…</body> 추출
function extractBody(html) {
  const m = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  return m ? m[1] : html;
}

// ── <style>…</style> 태그 전부 추출
function extractStyles(html) {
  const styles = [];
  const re = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  let m;
  while ((m = re.exec(html)) !== null) styles.push(m[1]);
  return styles.join('\n');
}

const style1 = extractStyles(html1);
const style2 = extractStyles(html2);
const body1  = extractBody(html1);
const body2  = extractBody(html2);

// ── 16:9 PPT 인쇄용 @page + 공통 오버라이드
const printCss = `
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');

/* ── PPT 16:9 페이지 설정 ── */
@page {
  size: 33.867cm 19.05cm;   /* 1920×1080 기준 16:9 */
  margin: 1.2cm 1.8cm;
}

* { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }

body {
  font-family: 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
  background: #F8FAFC;
  font-size: 11px;
  line-height: 1.55;
}

/* 섹션마다 새 페이지 */
.section, .toc-page { page-break-before: always; }
.cover { page-break-after: always; }

/* 두 번째 문서 시작 구분 */
.doc-separator {
  page-break-before: always;
  background: linear-gradient(135deg,#1E1B4B,#4F46E5);
  min-height: 19.05cm;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: white; text-align: center;
}
.doc-separator h2 { font-size: 28px; font-weight: 800; letter-spacing:-1px; margin-bottom:12px; }
.doc-separator p  { font-size: 14px; opacity: .7; }

/* 커버 전체화면 */
.cover {
  min-height: 19.05cm !important;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}

/* 레이아웃 컴팩트 조정 */
.section { padding: 28px 32px !important; }
.section-inner, .toc-inner { max-width: 100% !important; }
.container { padding: 28px 32px !important; }
.toc-page { padding: 28px 32px !important; }
.toc-grid { grid-template-columns: 1fr 1fr; gap: 8px !important; margin-top: 16px !important; }
.card-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)) !important; gap: 10px !important; }
.erd-grid  { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important; }
.stat-grid { grid-template-columns: repeat(4,1fr) !important; }

/* 폰트 크기 인쇄 조정 */
.cover h1   { font-size: 38px !important; }
.cover-sub  { font-size: 15px !important; }
.section-title { font-size: 18px !important; }
.sub-title  { font-size: 13px !important; }
h1          { font-size: 18px !important; }
h2          { font-size: 15px !important; }
h3          { font-size: 13px !important; }
p, td, li   { font-size: 11px !important; }
th          { font-size: 10px !important; }
.code-block { font-size: 10px !important; line-height: 1.5 !important; padding: 12px 16px !important; }

/* 페이지 안에서 요소 자르지 않기 */
table, .card, .erd-table, .code-block { page-break-inside: avoid; }

/* 여정/flow 가로 스크롤 제거 */
.journey-steps, .flow { flex-wrap: wrap !important; }
.arch { font-size: 10px !important; }

/* 마진 압축 */
.sub { margin-bottom: 18px !important; }
.tbl-wrap { margin-bottom: 10px !important; }
.highlight, .warn-box { padding: 10px 14px !important; font-size: 11px !important; }
`;

// ── 통합 HTML 생성
const combined = `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>청년 금융 혜택 통합 플랫폼 — 기획 및 개발 정의서</title>
<style>
/* ===== 기획정의서 스타일 ===== */
${style1}
/* ===== 개발상세정의서 스타일 ===== */
${style2}
/* ===== 인쇄/PDF 오버라이드 ===== */
${printCss}
</style>
</head>
<body>

<!-- ════════════════════════════════════
     제1부: 서비스 기획정의서
════════════════════════════════════ -->
${body1}

<!-- ════════════════════════════════════
     구분 슬라이드
════════════════════════════════════ -->
<div class="doc-separator">
  <h2>&#128295; 개발 상세 정의서</h2>
  <p>Technical Specification — 청년 금융 혜택 통합 플랫폼</p>
  <p style="margin-top:12px; opacity:.5; font-size:12px;">시스템 아키텍처 · API 명세 · DB 설계 · AI/RAG · 보안 · 배포</p>
</div>

<!-- ════════════════════════════════════
     제2부: 개발상세정의서
════════════════════════════════════ -->
${body2}

</body>
</html>`;

fs.writeFileSync(OUT_HTML, combined, 'utf8');
console.log('✅ 통합 HTML 생성:', OUT_HTML);

// ── Chrome 헤드리스 PDF 변환
const fileUrl = 'file:///' + OUT_HTML.replace(/\\/g, '/');
const cmd = [
  `"${CHROME}"`,
  '--headless=new',
  '--disable-gpu',
  '--no-sandbox',
  '--disable-dev-shm-usage',
  `--print-to-pdf="${OUT_PDF}"`,
  '--print-to-pdf-no-header',
  '--no-margins',
  '--run-all-compositor-stages-before-draw',
  '--virtual-time-budget=5000',
  `"${fileUrl}"`
].join(' ');

console.log('⏳ PDF 변환 중 (Chrome 헤드리스)...');
try {
  execSync(cmd, { timeout: 60000, stdio: 'pipe' });
  const stat = fs.statSync(OUT_PDF);
  console.log(`✅ PDF 생성 완료: ${OUT_PDF}`);
  console.log(`   파일 크기: ${(stat.size / 1024 / 1024).toFixed(2)} MB`);
} catch (e) {
  console.error('❌ PDF 변환 실패:', e.message);
  process.exit(1);
}
