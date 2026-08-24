const API = 'http://localhost:8000';
const byId = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => (
    {'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'}[char]
  ));
}

document.querySelectorAll('[data-example]').forEach((button) => {
  button.addEventListener('click', () => { byId('ticket').value = button.dataset.example; });
});

async function checkHealth() {
  const status = byId('health');
  try {
    const response = await fetch(`${API}/api/health`);
    if (!response.ok) throw new Error();
    const data = await response.json();
    status.className = 'status ok';
    status.textContent = data.llm_configured
      ? 'Backend доступен, Alice AI LLM настроена.'
      : 'Backend доступен, будет использован безопасный fallback.';
  } catch {
    status.className = 'status error';
    status.textContent = 'Backend недоступен. Запустите ./scripts/run-backend.sh';
  }
}

function renderResult(data) {
  const answered = data.status === 'answered';
  const decision = answered
    ? escapeHtml(data.answer)
    : `Автоответ запрещён. Тикет передан в очередь <strong>${escapeHtml(data.operator_queue)}</strong>.`;

  byId('result').className = 'result';
  byId('result').innerHTML = `
    <dl>
      <dt>ID тикета</dt><dd>${escapeHtml(data.ticket_id)}</dd>
      <dt>Тема</dt><dd>${escapeHtml(data.classification.topic)}</dd>
      <dt>Риск</dt><dd class="risk-${escapeHtml(data.classification.risk)}">${escapeHtml(data.classification.risk)}</dd>
      <dt>Уверенность</dt><dd>${Math.round(data.classification.confidence * 100)}%</dd>
      <dt>Маршрутизация</dt><dd>${data.routing_ms} мс</dd>
      <dt>Статус</dt><dd>${escapeHtml(data.status)}</dd>
    </dl>
    <div class="answer ${answered ? '' : 'escalated'}">${decision}</div>
    ${answered ? `<p class="muted">Источник: ${escapeHtml(data.answer_source)} · ${escapeHtml(data.knowledge_article)}</p>` : ''}
  `;
}

async function loadAudit() {
  const body = byId('audit');
  try {
    const response = await fetch(`${API}/api/audit?limit=10`);
    if (!response.ok) throw new Error();
    const data = await response.json();
    body.innerHTML = data.items.length
      ? data.items.map((item) => `
        <tr>
          <td>${escapeHtml(item.ticket_id)}</td>
          <td>${escapeHtml(item.classification.topic)}</td>
          <td class="risk-${escapeHtml(item.classification.risk)}">${escapeHtml(item.classification.risk)}</td>
          <td>${item.status === 'answered' ? 'автоответ' : `оператор: ${escapeHtml(item.operator_queue)}`}</td>
          <td>${item.routing_ms} мс</td>
        </tr>`).join('')
      : '<tr><td colspan="5" class="muted">Журнал пока пуст.</td></tr>';
  } catch {
    body.innerHTML = '<tr><td colspan="5" class="risk-high">Журнал недоступен.</td></tr>';
  }
}

byId('submit').addEventListener('click', async () => {
  const text = byId('ticket').value.trim();
  if (text.length < 3) {
    byId('result').textContent = 'Введите текст обращения.';
    return;
  }

  const button = byId('submit');
  button.disabled = true;
  button.textContent = 'Обработка…';
  try {
    const response = await fetch(`${API}/api/tickets/process`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text, channel: byId('channel').value}),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderResult(await response.json());
    await loadAudit();
  } catch (error) {
    byId('result').className = 'result status error';
    byId('result').textContent = `Ошибка: ${error.message}. Проверьте backend.`;
  } finally {
    button.disabled = false;
    button.textContent = 'Обработать тикет';
  }
});

checkHealth();
loadAudit();
byId('refresh').addEventListener('click', loadAudit);
