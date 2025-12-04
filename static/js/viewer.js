pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

let leftPdf = null, rightPdf = null;
let pageNum = 1;
let pageCount = 0;
let scale = 1.0;
let sync = true;
let textDiffActive = false;
let showLeftDiffs = true;
let diffOpacity = 1.0;

const leftCanvas = document.getElementById('leftCanvas');
const rightCanvas = document.getElementById('rightCanvas');
const leftCtx = leftCanvas.getContext('2d');
const rightCtx = rightCanvas.getContext('2d');

const leftOverlay = document.getElementById('leftOverlay');
const rightOverlay = document.getElementById('rightOverlay');
const leftOvCtx = leftOverlay.getContext('2d');
const rightOvCtx = rightOverlay.getContext('2d');

async function load() {
  leftPdf = await pdfjsLib.getDocument(LEFT_PDF).promise;
  rightPdf = await pdfjsLib.getDocument(RIGHT_PDF).promise;
  pageCount = Math.max(leftPdf.numPages, rightPdf.numPages);
  document.getElementById('pageCount').innerText = '/ ' + pageCount;
  renderPage(pageNum);
}

async function renderPage(num) {
  pageNum = Math.min(Math.max(1, num), pageCount);
  document.getElementById('pageNum').value = pageNum;

  // render left
  if (pageNum <= leftPdf.numPages) {
    const page = await leftPdf.getPage(pageNum);
    const viewport = page.getViewport({ scale });
    leftCanvas.width = viewport.width;
    leftCanvas.height = viewport.height;
    leftOverlay.width = viewport.width;
    leftOverlay.height = viewport.height;
    const renderContext = { canvasContext: leftCtx, viewport };
    await page.render(renderContext).promise;
    // ensure overlay displays at the same CSS size as the rendered canvas
    const leftRect = leftCanvas.getBoundingClientRect();
    leftOverlay.style.width = leftRect.width + 'px';
    leftOverlay.style.height = leftRect.height + 'px';
  } else {
    leftCtx.clearRect(0, 0, leftCanvas.width, leftCanvas.height);
  }

  // render right
  if (pageNum <= rightPdf.numPages) {
    const pageR = await rightPdf.getPage(pageNum);
    const viewportR = pageR.getViewport({ scale });
    rightCanvas.width = viewportR.width;
    rightCanvas.height = viewportR.height;
    rightOverlay.width = viewportR.width;
    rightOverlay.height = viewportR.height;
    const renderContextR = { canvasContext: rightCtx, viewport: viewportR };
    await pageR.render(renderContextR).promise;
    // ensure overlay displays at the same CSS size as the rendered canvas
    const rightRect = rightCanvas.getBoundingClientRect();
    rightOverlay.style.width = rightRect.width + 'px';
    rightOverlay.style.height = rightRect.height + 'px';
  } else {
    rightCtx.clearRect(0, 0, rightCanvas.width, rightCanvas.height);
  }

  // if automatic text-diff mode is enabled, request text diff for the new page
  if (textDiffActive) {
    // run but don't block UI
    requestTextDiff().then((r)=>{
      if (r && r.error) console.warn('textdiff request failed', r);
    });
  }
}


document.getElementById('prev').addEventListener('click', ()=>{ renderPage(pageNum-1); });
document.getElementById('next').addEventListener('click', ()=>{ renderPage(pageNum+1); });
document.getElementById('pageNum').addEventListener('change', (e)=>{ renderPage(parseInt(e.target.value)||1); });
document.getElementById('scale').addEventListener('input', (e)=>{ scale = parseFloat(e.target.value); renderPage(pageNum); });
document.getElementById('sync').addEventListener('change', (e)=>{ sync = e.target.checked; });
// removed pixel-diff controls; text diff handled separately

async function requestTextDiff() {
  try {
    const lfile = ('' + LEFT_PDF).split('/').pop();
    const rfile = ('' + RIGHT_PDF).split('/').pop();
    const url = `/textdiff?l=${encodeURIComponent(lfile)}&r=${encodeURIComponent(rfile)}&page=${pageNum}`;
    const res = await fetch(url);
    if (!res.ok) {
      const txt = await res.text();
      console.error('textdiff error', res.status, txt);
      return { error: true, status: res.status, text: txt };
    }
    const dataText = await res.text();
    const data = JSON.parse(dataText);

    // Clear previous box overlays
    const clearBoxes = (sideId) => {
      const side = document.getElementById(sideId);
      const prev = side.querySelectorAll('.td-box');
      prev.forEach(n => n.remove());
    };
    clearBoxes('leftSide');
    clearBoxes('rightSide');

    // Helper: create a box element in the `.side` container using normalized coords
    const applyAlpha = (rgbArray, baseAlpha) => {
      const sliderAlpha = Math.max(0, Math.min(1, diffOpacity));
      const effective = sliderAlpha === 0
        ? 0
        : Math.min(1, baseAlpha + (1 - baseAlpha) * sliderAlpha);
      return `rgba(${rgbArray.join(',')}, ${effective})`;
    };

    const makeBox = (sideId, boxObj, isRight=false) => {
      const side = document.getElementById(sideId);
      const canvas = side.querySelector('canvas');
      if (!canvas) return;
      const crect = canvas.getBoundingClientRect();
      const parentRect = side.getBoundingClientRect();

      const [nx0, ny0, nx1, ny1] = boxObj.box;
      const leftPx = (nx0 * crect.width) + (crect.left - parentRect.left);
      const topPx = (ny0 * crect.height) + (crect.top - parentRect.top);
      const wPx = (nx1 - nx0) * crect.width;
      const hPx = (ny1 - ny0) * crect.height;

      const div = document.createElement('div');
      div.className = 'td-box';
      div.style.position = 'absolute';
      div.style.left = Math.round(leftPx) + 'px';
      div.style.top = Math.round(topPx) + 'px';
      div.style.width = Math.max(2, Math.round(wPx)) + 'px';
      div.style.height = Math.max(2, Math.round(hPx)) + 'px';
      div.style.pointerEvents = 'none';
      div.style.boxSizing = 'border-box';
      div.style.border = 'none';

      if (isRight) {
        const c = Math.max(0, Math.min(5, boxObj.dashCount || 0));
        if (boxObj.improved) {
          div.style.backgroundColor = applyAlpha([67, 160, 71], 0.12);
        } else if (c === 0) {
          div.style.backgroundColor = applyAlpha([25, 118, 210], 0.08);
        } else {
          const t = Math.min(1, c / 5);
          const lerp = (a,b,t)=> Math.round(a + (b-a)*t);
          const yellow = [255, 213, 79];
          const red = [211, 47, 47];
          const rgb = [ lerp(yellow[0], red[0], t), lerp(yellow[1], red[1], t), lerp(yellow[2], red[2], t) ];
          const baseAlpha = 0.08 + 0.25 * t;
          div.style.backgroundColor = applyAlpha(rgb, baseAlpha);
        }
      } else {
        div.style.backgroundColor = applyAlpha([30, 136, 229], 0.08);
      }

      div.title = boxObj.text || '';
      side.appendChild(div);
    };

    (data.left || []).forEach(b => { if (showLeftDiffs) makeBox('leftSide', b, false); });
    (data.right || []).forEach(b => makeBox('rightSide', b, true));

    return { error: false };
  } catch (err) {
    console.error('text diff error', err);
    return { error: true, text: err.message };
  }
}

// toggle text diff mode and run on demand
const textDiffBtn = document.getElementById('textDiff');
textDiffBtn.addEventListener('click', async (e) => {
  textDiffActive = !textDiffActive;
  textDiffBtn.textContent = textDiffActive ? 'Text Diff (on)' : 'Text Diff';
  if (textDiffActive) await requestTextDiff();
  else {
    const clearBoxes = (sideId) => {
      const side = document.getElementById(sideId);
      const prev = side.querySelectorAll('.td-box');
      prev.forEach(n => n.remove());
    };
    clearBoxes('leftSide');
    clearBoxes('rightSide');
  }
});

// toggle left diffs visibility
const showLeftCheckbox = document.getElementById('showLeft');
showLeftCheckbox.addEventListener('change', async (e) => {
  showLeftDiffs = e.target.checked;
  if (textDiffActive) await requestTextDiff();
});

// opacity slider for diff boxes
const boxOpacityInput = document.getElementById('boxOpacity');
const boxOpacityVal = document.getElementById('boxOpacityVal');
const updateOpacityLabel = () => {
  boxOpacityVal.textContent = Math.round(diffOpacity * 100) + '%';
};
updateOpacityLabel();
boxOpacityInput.addEventListener('input', async (e) => {
  diffOpacity = parseFloat(e.target.value);
  updateOpacityLabel();
  if (textDiffActive) await requestTextDiff();
});

// optional: keyboard shortcuts
window.addEventListener('keydown', (e)=>{
  if (e.key === 'ArrowRight') renderPage(pageNum+1);
  if (e.key === 'ArrowLeft') renderPage(pageNum-1);
});

load().catch(err=>{ console.error(err); alert('Error loading PDFs: '+err.message); });

// Threshold control: update label and recompute when changed
// pixel-diff controls removed
