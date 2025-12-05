(function(){
  const form = document.getElementById('cmmForm');
  const statusEl = document.getElementById('status');
  const resultsSection = document.getElementById('results');
  const summaryEl = document.getElementById('summary');
  const tableBody = document.querySelector('#resultsTable tbody');

  function setStatus(message, isError=false) {
    statusEl.textContent = message;
    statusEl.style.color = isError ? '#c62828' : '#555';
  }

  function formatDeviation(value) {
    if (value === null || value === undefined) return '—';
    const num = Number(value);
    if (Number.isNaN(num)) return '—';
    const cls = num > 0 ? 'deviation-positive' : num < 0 ? 'deviation-negative' : 'deviation-neutral';
    return `<span class="${cls}">${num.toFixed(4)}</span>`;
  }

  function parseNumeric(value) {
    if (value === null || value === undefined) return NaN;
    if (typeof value === 'string' && value.trim() === '') return NaN;
    const num = Number(value);
    return Number.isFinite(num) ? num : NaN;
  }

  function firstNumeric(values) {
    for (const v of values) {
      const num = parseNumeric(v);
      if (Number.isFinite(num)) return num;
    }
    return null;
  }

  function isOutOfTolerance(points) {
    if (!points || !points.length) return false;
    for (const pt of points) {
      const nominal = parseNumeric(pt.nominal);
      const actual = parseNumeric(pt.actual);
      const deviation = parseNumeric(pt.deviation);

      const upper = parseNumeric(pt.upperTol);
      const lower = parseNumeric(pt.lowerTol);

      const hasActual = Number.isFinite(nominal) && Number.isFinite(actual);
      const hasUpper = Number.isFinite(upper);
      const hasLower = Number.isFinite(lower);

      if (hasActual) {
        if (hasUpper && actual > nominal + upper) return true;
        if (hasLower && actual < nominal + lower) return true;
      } else {
        if (!Number.isNaN(deviation)) {
          if (hasUpper && deviation > upper) return true;
          if (hasLower && deviation < lower) return true;
        }
      }
    }
    return false;
  }

  let tooltipEl;

  function getTooltip() {
    if (!tooltipEl) {
      tooltipEl = document.createElement('div');
      tooltipEl.className = 'sparkline-tooltip';
      document.body.appendChild(tooltipEl);
    }
    return tooltipEl;
  }

  function showTooltip(canvas, text, x, y) {
    const tooltip = getTooltip();
    tooltip.textContent = text;
    const rect = canvas.getBoundingClientRect();
    tooltip.style.left = `${rect.left + x + window.scrollX + 8}px`;
    tooltip.style.top = `${rect.top + y + window.scrollY - tooltip.offsetHeight - 6}px`;
    tooltip.style.opacity = '1';
  }

  function hideTooltip() {
    if (tooltipEl) tooltipEl.style.opacity = '0';
  }

  function attachHover(canvas) {
    canvas.addEventListener('mousemove', (event) => {
      const points = canvas._sparklinePoints || [];
      if (!points.length) return hideTooltip();

      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const hit = points.find(pt => {
        const dx = pt.x - x;
        const dy = pt.y - y;
        return Math.hypot(dx, dy) <= 6;
      });

      if (hit) {
        showTooltip(canvas, hit.label, hit.x, hit.y);
      } else {
        hideTooltip();
      }
    });

    canvas.addEventListener('mouseleave', hideTooltip);
  }

  function renderSparkline(canvas, points) {
    if (!canvas || !points || points.length === 0) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = 140;
    const height = canvas.height = 36;

    const plottedPoints = points
      .map((p, idx) => {
        const deviation = parseNumeric(p.deviation);
        if (!Number.isFinite(deviation)) return null;
        return { deviation, report: p.report || `Report ${idx + 1}` };
      })
      .filter(Boolean);

    const deviationValues = plottedPoints.map(p => p.deviation);
    const upperTol = firstNumeric(points.map(p => p.upperTol));
    const lowerTol = firstNumeric(points.map(p => p.lowerTol));
    const outOfTolerance = isOutOfTolerance(points);

    const domainValues = deviationValues.slice();
    if (upperTol !== null) domainValues.push(upperTol);
    if (lowerTol !== null) domainValues.push(lowerTol);
    const values = domainValues;
    if (values.length === 0) return;

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = (max - min) || 1;

    ctx.clearRect(0, 0, width, height);

    if (outOfTolerance) {
      ctx.save();
      ctx.fillStyle = '#fdecea';
      ctx.fillRect(0, 0, width, height);
      ctx.restore();
      canvas.classList.add('sparkline-out-of-tolerance');
    } else {
      canvas.classList.remove('sparkline-out-of-tolerance');
    }

    ctx.strokeStyle = '#1e88e5';
    ctx.lineWidth = 2;
    ctx.beginPath();

    const pointMeta = [];
    plottedPoints.forEach((pt, idx) => {
      const x = deviationValues.length === 1 ? width / 2 : (idx / (deviationValues.length - 1)) * (width - 6) + 3;
      const y = height - ((pt.deviation - min) / range) * (height - 6) - 3;
      pointMeta.push({ x, y, label: pt.report });
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.fillStyle = '#1e88e5';
    plottedPoints.forEach((pt, idx) => {
      const x = deviationValues.length === 1 ? width / 2 : (idx / (deviationValues.length - 1)) * (width - 6) + 3;
      const y = height - ((pt.deviation - min) / range) * (height - 6) - 3;
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw baseline at 0 if within range
    if (min <= 0 && max >= 0) {
      const zeroY = height - ((0 - min) / range) * (height - 6) - 3;
      ctx.strokeStyle = '#9e9e9e';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(0, zeroY);
      ctx.lineTo(width, zeroY);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    const drawTolerance = (value, color) => {
      if (value === null) return;
      const y = height - ((value - min) / range) * (height - 6) - 3;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 3]);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
      ctx.setLineDash([]);
    };

    drawTolerance(upperTol, '#c62828');
    drawTolerance(lowerTol, '#2e7d32');

    canvas._sparklinePoints = pointMeta;
    if (!canvas._sparklineHoverAttached) {
      attachHover(canvas);
      canvas._sparklineHoverAttached = true;
    }
  }

  function renderTable(data) {
    tableBody.innerHTML = '';
    const features = data.features || [];

    if (!features.length) {
      setStatus('No feature rows were found with the current filters.', false);
      resultsSection.hidden = true;
      return false;
    }

    features.forEach(feature => {
      const row = document.createElement('tr');
      const outOfTolerance = isOutOfTolerance(feature.points || []);

      if (outOfTolerance) {
        row.classList.add('cmm-row-out-of-tolerance');
      }

      const nameCell = document.createElement('td');
      nameCell.textContent = feature.name;
      row.appendChild(nameCell);

      const deviationCell = document.createElement('td');
      deviationCell.innerHTML = formatDeviation(feature.latest);
      row.appendChild(deviationCell);

      const trendCell = document.createElement('td');
      if (feature.points && feature.points.length) {
        const canvas = document.createElement('canvas');
        canvas.className = 'sparkline';
        renderSparkline(canvas, feature.points);
        trendCell.appendChild(canvas);
      } else {
        trendCell.textContent = 'No data';
      }
      row.appendChild(trendCell);

      tableBody.appendChild(row);
    });

    let summary = `Features: ${features.length}`;
    if (typeof data.reportsAnalyzed === 'number') {
      summary += ` • Reports analyzed: ${data.reportsAnalyzed}`;
    }
    if (data.errors && data.errors.length) {
      summary += ` • ${data.errors.length} files skipped`;
    }
    summaryEl.textContent = summary;
    resultsSection.hidden = false;
    return true;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
      folder: form.folder.value.trim(),
      startDate: form.startDate.value || null,
      endDate: form.endDate.value || null,
      partType: form.partType.value || null,
      dieNumber: form.dieNumber.value.trim() || null,
    };

    if (!payload.folder) {
      setStatus('Please enter a folder path.', true);
      return;
    }

    setStatus('Scanning reports...', false);

    try {
      const response = await fetch('/api/cmm_summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const text = await response.text();
      if (!response.ok) {
        setStatus(`Error: ${text}`, true);
        resultsSection.hidden = true;
        return;
      }

      const data = JSON.parse(text || '{}');
      const hasFeatures = renderTable(data);

      if (data.errors && data.errors.length) {
        setStatus(`Completed with ${data.errors.length} skipped file(s).`, false);
      } else if (hasFeatures) {
        setStatus('Complete.', false);
      }
    } catch (err) {
      setStatus(`Request failed: ${err.message}`, true);
      resultsSection.hidden = true;
    }
  });
})();
