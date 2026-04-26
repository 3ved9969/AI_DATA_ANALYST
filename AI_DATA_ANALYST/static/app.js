function addMessage(text, cls) {
  const chatBox = document.getElementById("chatBox");
  const div = document.createElement("div");
  div.className = `message ${cls}`;
  div.textContent = text;
  chatBox.appendChild(div);
}

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const status = document.getElementById("uploadStatus");
  if (!fileInput.files.length) {
    status.textContent = "Please choose a file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  const res = await fetch("/upload", {
    method: "POST",
    body: formData,
  });
  const data = await res.json();

  if (data.error) {
    status.textContent = data.error;
    return;
  }

  status.textContent = data.message;
  addMessage("Dataset uploaded successfully.", "bot");
}
function renderTable(columns, rows) {
  const container = document.getElementById("tableContainer");
  if (!rows || !rows.length) {
    container.innerHTML = "<p>No rows to display.</p>";
    return;
  }

  let html = "<table><thead><tr>";
  columns.forEach(col => html += `<th>${col}</th>`);
  html += "</tr></thead><tbody>";

  rows.forEach(row => {
    html += "<tr>";
    columns.forEach(col => html += `<td>${row[col] ?? ""}</td>`);
    html += "</tr>";
  });

  html += "</tbody></table>";
  container.innerHTML = html;
}

function renderInsight(insight, reportUrl) {
  const container = document.getElementById("insightContainer");
  container.innerHTML = `
    <h3>${insight.headline || "Insight"}</h3>
    <p><strong>Insight:</strong> ${insight.insight || ""}</p>
    <p><strong>Possible Reason:</strong> ${insight.possible_reason || ""}</p>
    <p><strong>Recommendation:</strong> ${insight.recommendation || ""}</p>
    <p><a href="${reportUrl}" target="_blank">Download Report</a></p>
  `;
}

function renderChart(chartUrl) {
  const container = document.getElementById("chartContainer");
  if (!chartUrl) {
    container.innerHTML = "<p>No chart generated for this query.</p>";
    return;
  }
  container.innerHTML = `<iframe src="${chartUrl}"></iframe>`;
}

async function sendQuery() {
  const input = document.getElementById("questionInput");
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  const res = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const data = await res.json();
  if (data.error) {
    addMessage(data.error, "bot");
    return;
  }
  addMessage(data.insight?.insight || "Analysis completed.", "bot");
  renderTable(data.columns, data.result);
  renderChart(data.chart_url);
  renderInsight(data.insight, data.report_url);
}