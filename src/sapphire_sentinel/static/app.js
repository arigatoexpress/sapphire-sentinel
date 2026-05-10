let data = null;
let activeDecision = null;

function text(id, value) {
  document.getElementById(id).textContent = value ?? '';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function shortHash(value) {
  return value ? `${value.slice(0, 10)}...${value.slice(-8)}` : '';
}

function txLink(record, fallback = '') {
  if (!record || !record.explorer) return escapeHtml(fallback || 'pending');
  const label = record.tx_hash ? shortHash(record.tx_hash) : record.explorer;
  return `<a href="${escapeHtml(record.explorer)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
}

function linkOrText(href, label) {
  if (!href || !String(href).startsWith('http')) return escapeHtml(label || href || 'pending');
  return `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label || href)}</a>`;
}

function amount(value) {
  return `${(Number(value || 0) / 1000000).toFixed(6)} USDC`;
}

function traceFor(decision) {
  const status = decision.approved ? 'Allowed' : 'Blocked';
  const reasons = decision.reasons.map((reason) => escapeHtml(reason)).join('; ');
  return [
    ['1', 'Mandate check', `${status}: ${reasons}`],
    ['2', 'x402 quote binding', `${decision.payment_requirements.network} ${amount(decision.payment_requirements.amount)} to ${decision.payment_requirements.payTo}`],
    ['3', 'Privacy commitment', decision.privacy_commitment],
    ['4', 'Robinhood receipt', decision.chain_anchor.record_tx_hash ? `anchored ${decision.chain_anchor.record_tx_hash}` : `${decision.chain_anchor.contract} nonce ${decision.decision_nonce}`],
  ];
}

function renderDecision(decision) {
  activeDecision = decision;
  const state = document.getElementById('state');
  state.textContent = decision.approved ? 'APPROVED' : 'BLOCKED';
  state.className = `state ${decision.approved ? 'approved' : 'blocked'}`;
  text('receipt', decision.receipt_id);
  document.getElementById('trace').innerHTML = traceFor(decision).map((step) => `
    <div class="trace-step">
      <div class="dot">${step[0]}</div>
      <div>
        <div class="trace-title">${escapeHtml(step[1])}</div>
        <div class="trace-copy">${escapeHtml(step[2])}</div>
      </div>
    </div>
  `).join('');

  const req = decision.payment_requirements;
  text('resource', req.resource);
  text('network', req.network);
  text('asset', req.asset);
  text('amount', amount(req.amount));
  text('payto', req.payTo);
  text('facilitator', decision.http_402.extensions.sentinel.facilitator);

  const anchor = decision.chain_anchor;
  document.getElementById('deployed').innerHTML = anchor.contract_address
    ? `${linkOrText(anchor.explorer, anchor.contract_address)} (${linkOrText(anchor.tx_explorer, shortHash(anchor.tx_hash))})`
    : 'pending deployment';
  document.getElementById('verified').innerHTML = anchor.source_verified
    ? `${linkOrText(anchor.explorer, `true (${anchor.compiler_version})`)}`
    : 'pending source verification';
  text('policy', anchor.mandate_policy_hash);
  text('result', anchor.result_hash);
  text('risk', anchor.risk_hash);
  text('privacy', anchor.privacy_commitment);
  text('nonce', anchor.decision_nonce);
  text('broadcast', `${anchor.broadcast} (${anchor.mode})`);
  document.getElementById('record-tx').innerHTML = linkOrText(anchor.record_tx_explorer, anchor.record_tx_hash ? shortHash(anchor.record_tx_hash) : 'preview only');
  text('chain-remaining', anchor.onchain_remaining_usdc ? `${anchor.onchain_remaining_usdc} USDC` : 'pending');
  renderEvents(anchor.demo_events || {});
  text('order-draft', JSON.stringify(decision.order_draft.primary_draft, null, 2));
}

function renderEvents(events) {
  document.getElementById('event-mandate').innerHTML = txLink(events.register_mandate);
  document.getElementById('event-seed').innerHTML = txLink(events.seed_prior_spend);
  document.getElementById('event-approved').innerHTML = txLink(events.approved_receipt);
  document.getElementById('event-blocked').innerHTML = txLink(events.blocked_receipt);
}

function renderScenarios() {
  const list = document.getElementById('scenario-list');
  list.innerHTML = data.attack_scenarios.map((scenario, index) => `
    <button class="scenario ${index === 0 ? 'active' : ''}" data-scenario="${escapeHtml(scenario.id)}">
      <span>
        <span class="scenario-title">${escapeHtml(scenario.title)}</span>
        <span class="scenario-sub">${escapeHtml(scenario.attacker_move)}</span>
      </span>
      <span class="pill ${scenario.approved ? 'ok' : 'block'}">${scenario.approved ? 'allow' : 'block'}</span>
    </button>
  `).join('');
  list.querySelectorAll('.scenario').forEach((button) => {
      button.addEventListener('click', () => {
      list.querySelectorAll('.scenario').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      const scenario = data.attack_scenarios.find((item) => item.id === button.dataset.scenario);
      const decision = scenario.decision || (scenario.approved ? data.approved_flow : data.blocked_flow);
      fillAttemptForm(scenario.attempt || {});
      renderDecision(decision);
      renderEvalOutput(decision, 'scenario');
    });
  });
}

function fillAttemptForm(attempt) {
  if (attempt.resource) document.getElementById('eval-resource').value = attempt.resource;
  if (attempt.amount_usdc) document.getElementById('eval-amount').value = attempt.amount_usdc;
  if (attempt.payload_summary) document.getElementById('eval-summary').value = attempt.payload_summary;
}

function renderPrivacy() {
  document.getElementById('privacy-list').innerHTML = data.privacy_attestations.map((item) => `
    <div class="privacy-row">
      <strong>${escapeHtml(item.engine)}</strong>
      <span>${escapeHtml(item.public_claim)}</span>
      <span>${escapeHtml(item.commitment)}</span>
    </div>
  `).join('');
}

function renderPrivacyProofs() {
  document.getElementById('privacy-proof-list').innerHTML = data.privacy_proofs.artifacts.map((item) => `
    <div class="proof-row">
      <span>
        <strong>${escapeHtml(item.engine)}</strong>
        <span>${escapeHtml(item.exported_commitment)}</span>
        <span>${escapeHtml(item.artifact_path)}</span>
      </span>
      <span class="pill ok">${escapeHtml(item.status)}</span>
    </div>
  `).join('');
}

function renderScorecard() {
  document.getElementById('scorecard').innerHTML = data.judging_scorecard.map((item) => `
    <div class="score-row">
      <strong>${escapeHtml(item.criterion)}</strong>
      <span>${escapeHtml(item.evidence)}</span>
    </div>
  `).join('');
}

function renderProofPoints() {
  document.getElementById('proof-list').innerHTML = data.proof_points.map((item) => `
    <div class="proof-row">
      <span>
        <strong>${escapeHtml(item.label)}</strong>
        <span>${linkOrText(item.evidence, item.evidence || item.status)}</span>
      </span>
      <span class="pill ${item.status === 'disabled' ? 'block' : 'ok'}">${escapeHtml(item.status)}</span>
    </div>
  `).join('');
}

function renderNetworks() {
  document.getElementById('network-list').innerHTML = data.network_matrix.map((item) => `
    <div class="matrix-row">
      <span>
        <strong>${escapeHtml(item.name)}</strong>
        <small>${escapeHtml(item.role)} | ${escapeHtml(item.caip2 || 'non-evm/private')}</small>
        <small>${escapeHtml(item.next_action)}</small>
      </span>
      <span class="tag">${escapeHtml(item.status)}</span>
    </div>
  `).join('');
}

function renderRoadmap() {
  document.getElementById('roadmap-list').innerHTML = data.integration_roadmap.map((item) => `
    <div class="matrix-row">
      <span>
        <strong>${escapeHtml(item.label)}</strong>
        <small>${escapeHtml(item.proof)}</small>
        <small>${escapeHtml(item.boundary)}</small>
      </span>
      <span class="tag">${escapeHtml(item.status)}</span>
    </div>
  `).join('');
}

function renderMirrors() {
  document.getElementById('mirror-list').innerHTML = data.receipt_mirrors.map((item) => `
    <div class="matrix-row">
      <span>
        <strong>${escapeHtml(item.name)}</strong>
        <small>${escapeHtml(item.role)} | ${escapeHtml(item.caip2 || 'non-evm')}</small>
        <small>${item.contract_address ? linkOrText(item.explorer, item.contract_address) : escapeHtml(item.claim_boundary)}</small>
      </span>
      <span class="tag">${escapeHtml(item.status)}</span>
    </div>
  `).join('');
}

function renderMegaethMainnet() {
  const scout = data.megaeth_mainnet_agent;
  const policy = scout.policy;
  text('megaeth-mainnet-network', `${scout.network.name} ${scout.network.chain_id}`);
  text('megaeth-mainnet-policy', `${policy.mode} | sign=${policy.can_sign} | send=${policy.can_send_transactions}`);
  text('megaeth-mainnet-tokens', Object.entries(scout.tokens).map(([symbol, address]) => `${symbol}:${address}`).join(' | '));
  document.getElementById('megaeth-app-list').innerHTML = scout.apps.slice(0, 10).map((item) => `
    <div class="matrix-row">
      <span>
        <strong>${linkOrText(item.url, item.name)}</strong>
        <small>${escapeHtml(item.category.join(', '))} | ${escapeHtml(item.status)}</small>
        <small>${escapeHtml(item.agent_strategy)}</small>
      </span>
      <span class="tag">${escapeHtml(item.execution_policy)}</span>
    </div>
  `).join('');
}

async function evaluateResource(overrides = null) {
  const payload = overrides || {
    resource: document.getElementById('eval-resource').value,
    amount_usdc: document.getElementById('eval-amount').value,
    action: 'buy-private-signal',
    payload_summary: document.getElementById('eval-summary').value,
    result_summary: 'private basket risk passes single-issuer and drawdown caps'
  };
  const response = await fetch('/api/evaluate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const body = await response.json();
  renderEvalOutput(body.decision, body.mode);
  if (overrides) renderDecision(body.decision);
}

function renderEvalOutput(decision, mode) {
  text('eval-output', JSON.stringify({
    approved: decision.approved,
    risk_flags: decision.risk_flags,
    receipt_id: decision.receipt_id,
    privacy_commitment: decision.privacy_commitment,
    mode,
    anchor_mode: decision.chain_anchor.mode,
    onchain_recorded: decision.chain_anchor.onchain_recorded
  }, null, 2));
}

async function load() {
  const response = await fetch('/api/demo');
  data = await response.json();
  text('thesis', data.project.thesis);
  text('chain', `${data.project.primary_chain} ${data.project.chain_id}`);
  text('payment', data.project.settlement_network);
  text('budget', `$${data.mandate.remaining_usdc} / $${data.mandate.max_spend_usdc}`);
  text('contract-kpi', data.approved_flow.chain_anchor.contract_address || data.approved_flow.chain_anchor.contract);
  text('mode', `${data.project.mode} | ${data.attack_scenarios.filter((item) => item.passed).length}/${data.attack_scenarios.length} checks`);
  renderScenarios();
  renderPrivacy();
  renderPrivacyProofs();
  renderScorecard();
  renderProofPoints();
  renderNetworks();
  renderRoadmap();
  renderMirrors();
  renderMegaethMainnet();
  renderDecision(data.approved_flow);
  evaluateResource();
}

document.getElementById('eval-button').addEventListener('click', () => evaluateResource());
load();

