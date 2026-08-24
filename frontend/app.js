const API = 'http://localhost:8000';
const $ = (id) => document.getElementById(id);

document.querySelectorAll('[data-example]').forEach((button) => {
  button.addEventListener('click', () => { $('ticket').value = button.dataset.example; });
});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}

async function checkHealth() {
  try {
    const response = await fetch(`${API}/api/health`);
    const data = await response.json();
    document.querySelector('.health').classList.add('ok');
    $('healthText').textContent = data.llm_configured ? 'API · Alice AI LLM подключена' : 'API · безопасный fallback';
  } catch { $('healthText').textContent = 'API недоступен'; }
}

function renderResult(data) {
  const risk = data.classification.risk;
  const answered = data.status === 'answered';
  $('result').innerHTML = `<div class="result-content">
    <div class="decision-top"><div><span class="eyebrow">${answered ? 'АВТООТВЕТ' : 'ЭСКАЛАЦИЯ'}</span><h2>${answered ? 'Можно ответить' : 'Нужен оператор'}</h2></div><span class="badge ${risk}">${risk} risk</span></div>
    <div class="facts"><div class="fact"><small>Тема</small><strong>${escapeHtml(data.classification.topic)}</strong></div><div class="fact"><small>Уверенность</small><strong>${Math.round(data.classification.confidence * 100)}%</strong></div><div class="fact"><small>Маршрут</small><strong>${data.routing_ms} мс</strong></div></div>
    <div class="answer ${answered ? '' : 'escalated'}">${answered ? escapeHtml(data.answer) : `Автоответ заблокирован. Тикет направлен в очередь <b>${escapeHtml(data.operator_queue)}</b>.`}</div>
    <div class="source">${answered ? `Источник: ${escapeHtml(data.answer_source)} · ${escapeHtml(data.knowledge_article)}` : `Причина: ${escapeHtml(data.classification.reasons.join(', '))}`} · ${escapeHtml(data.ticket_id)}</div>
  </div>`;
}

$('submit').addEventListener('click', async () => {
  const text = $('ticket').value.trim();
  if (text.length < 3) return;
  $('submit').disabled = true; $('submit').textContent = 'Анализируем…';
  try {
    const response = await fetch(`${API}/api/tickets/process`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text, channel:$('channel').value})});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderResult(await response.json()); await loadAudit();
  } catch (error) { $('result').innerHTML = `<div class="empty"><h2>Не удалось обработать</h2><p>${escapeHtml(error.message)}. Проверьте, запущен ли backend.</p></div>`; }
  finally { $('submit').disabled = false; $('submit').innerHTML = 'Обработать <span>→</span>'; }
});

async function loadAudit() {
  try {
    const data = await (await fetch(`${API}/api/audit?limit=8`)).json();
    $('audit').innerHTML = data.items.length ? data.items.map((item) => `<div class="audit-item"><strong>${escapeHtml(item.ticket_id)}</strong><span>${escapeHtml(item.classification.topic)}</span><span class="badge ${item.classification.risk}">${item.classification.risk}</span><span>${item.routing_ms} мс</span></div>`).join('') : '<div class="audit-empty">История пока пуста</div>';
  } catch { $('audit').innerHTML = '<div class="audit-empty">Журнал недоступен</div>'; }
}

$('refresh').addEventListener('click', loadAudit);
checkHealth(); loadAudit();
