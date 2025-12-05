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

  function renderSparkline(canvas, points) {
    if (!canvas || !points || points.length === 0) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = 140;
    const height = canvas.height = 36;

    const values = points.map(p => Number(p.deviation)).filter(v => !Number.isNaN(v));
    if (values.length === 0) return;

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = (max - min) || 1;

    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = '#1e88e5';
    ctx.lineWidth = 2;
    ctx.beginPath();

    values.forEach((v, idx) => {
      const x = values.length === 1 ? width / 2 : (idx / (values.length - 1)) * (width - 6) + 3;
      const y = height - ((v - min) / range) * (height - 6) - 3;
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

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
