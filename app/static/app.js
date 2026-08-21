const form = document.querySelector("#ask-form");
const questionInput = document.querySelector("#question");
const messageList = document.querySelector("#message-list");
const sendButton = document.querySelector("#send-button");
const newChatButton = document.querySelector("#new-chat");
const referenceTemplate = document.querySelector("#reference-template");
const knowledgeStatus = document.querySelector("#knowledge-status");
const rebuildKnowledgeButton = document.querySelector("#rebuild-knowledge");
const managerToggleButton = document.querySelector("#knowledge-manager-toggle");
const knowledgeManager = document.querySelector("#knowledge-manager");
const searchForm = document.querySelector("#knowledge-search-form");
const searchInput = document.querySelector("#knowledge-query");
const searchStatus = document.querySelector("#search-status");
const searchResults = document.querySelector("#search-results");
const entryStatus = document.querySelector("#entry-status");
const uploadForm = document.querySelector("#upload-form");
const uploadFile = document.querySelector("#upload-file");
const editDialog = document.querySelector("#edit-dialog");
const editForm = document.querySelector("#edit-form");
const editTitle = document.querySelector("#edit-title");
const editFields = document.querySelector("#edit-fields");
const editStatus = document.querySelector("#edit-status");
const historyList = document.querySelector("#history-list");
const refreshHistoryButton = document.querySelector("#refresh-history");
const feedbackDashboardToggle = document.querySelector("#feedback-dashboard-toggle");
const qualityDashboard = document.querySelector("#quality-dashboard");
const refreshFeedbackButton = document.querySelector("#refresh-feedback");
const dashboardStatus = document.querySelector("#dashboard-status");
const feedbackMetrics = document.querySelector("#feedback-metrics");
const commonReasons = document.querySelector("#common-reasons");
const recommendedActions = document.querySelector("#recommended-actions");
const recentFeedbackList = document.querySelector("#recent-feedback-list");
const reviewStatus = document.querySelector("#review-status");
const reviewResults = document.querySelector("#review-results");
const refreshReviewQueueButton = document.querySelector("#refresh-review-queue");
const versionStatus = document.querySelector("#version-status");
const versionResults = document.querySelector("#version-results");
const refreshKnowledgeVersionsButton = document.querySelector("#refresh-knowledge-versions");
const runRagEvaluationButton = document.querySelector("#run-rag-evaluation");
const compareRetrievalButton = document.querySelector("#compare-retrieval");
const diagnoseRetrievalButton = document.querySelector("#diagnose-retrieval");
const evaluationStatus = document.querySelector("#evaluation-status");
const evaluationMetrics = document.querySelector("#evaluation-metrics");
const evaluationResults = document.querySelector("#evaluation-results");
const evaluationQualityGate = document.querySelector("#evaluation-quality-gate");
const refreshEvaluationHistoryButton = document.querySelector("#refresh-evaluation-history");
const evaluationHistoryStatus = document.querySelector("#evaluation-history-status");
const evaluationHistoryList = document.querySelector("#evaluation-history-list");
const customEvaluationForm = document.querySelector("#custom-evaluation-form");
const customEvaluationQuestion = document.querySelector("#evaluation-question");
const customEvaluationExpectedName = document.querySelector("#evaluation-expected-name");
const customEvaluationAlternativeNames = document.querySelector("#evaluation-alternative-names");
const customEvaluationCategory = document.querySelector("#evaluation-category");
const customEvaluationExpectedType = document.querySelector("#evaluation-expected-type");
const customEvaluationStatus = document.querySelector("#custom-evaluation-status");
const customEvaluationList = document.querySelector("#custom-evaluation-list");
const comparisonStatus = document.querySelector("#comparison-status");
const comparisonMetrics = document.querySelector("#comparison-metrics");
const comparisonResults = document.querySelector("#comparison-results");
const diagnosisStatus = document.querySelector("#diagnosis-status");
const diagnosisMetrics = document.querySelector("#diagnosis-metrics");
const diagnosisResults = document.querySelector("#diagnosis-results");

const SOURCE_TIER_OPTIONS = [
  ["authority", "权威机构"],
  ["professional", "专业机构"],
  ["general", "一般资料"],
  ["unverified", "待核实"],
];

const entryConfiguration = {
  condition: {
    endpoint: "/conditions",
    label: "病症",
    fields: [
      ["name", "病症名称", "input"],
      ["symptoms", "常见症状", "textarea"],
      ["treatment", "通用处理建议", "textarea"],
      ["source", "资料来源", "input"],
      ["source_tier", "可信度等级", "select"],
    ],
  },
  drug: {
    endpoint: "/drugs",
    label: "药物",
    fields: [
      ["name", "药物名称", "input"],
      ["effects", "药物作用", "textarea"],
      ["instructions", "使用说明", "textarea"],
      ["source", "资料来源", "input"],
      ["source_tier", "可信度等级", "select"],
    ],
  },
  document: {
    endpoint: "/documents",
    label: "资料",
    fields: [
      ["title", "资料标题", "input"],
      ["source", "资料来源", "input"],
      ["source_tier", "可信度等级", "select"],
      ["content", "资料内容", "textarea"],
    ],
  },
};

let activeEdit = null;

const ACTIVE_CONVERSATION_KEY = "medical-health-active-conversation";
let conversationId = localStorage.getItem(ACTIVE_CONVERSATION_KEY) || createConversationId();

function createConversationId() {
  return `web-${crypto.randomUUID()}`;
}

function saveActiveConversation() {
  localStorage.setItem(ACTIVE_CONVERSATION_KEY, conversationId);
}

function scrollToLatestMessage() {
  messageList.scrollTop = messageList.scrollHeight;
}

function getSourceTierLabel(sourceTier) {
  return SOURCE_TIER_OPTIONS.find(([value]) => value === sourceTier)?.[1] || "待核实";
}

function formatUpdatedAt(updatedAt) {
  if (!updatedAt) return "未记录";
  const parsed = new Date(updatedAt);
  if (Number.isNaN(parsed.getTime())) return "未记录";
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsed);
}

function getKnowledgeTypeLabel(type) {
  return ({ condition: "病症", drug: "药物", document: "资料" })[type] || type;
}

function getSnapshotReasonLabel(reason) {
  return ({
    rebuild: "重建时自动保存",
    pre_restore: "恢复前自动备份",
  })[reason] || "自动保存";
}

function appendMessage(content, role, references = [], assistantMessageId = null) {
  const message = document.createElement("article");
  message.className = `message ${role}`;

  if (role === "assistant") {
    const label = document.createElement("p");
    label.className = "message-label";
    label.textContent = "医疗健康助手";
    message.append(label);
  }

  const text = document.createElement("p");
  text.className = "message-content";
  text.textContent = content;
  message.append(text);

  appendReferences(message, references);
  appendFeedback(message, role, assistantMessageId);

  messageList.append(message);
  scrollToLatestMessage();
  return message;
}

function appendReferences(message, references) {
  if (references.length === 0) return;
  const referenceSection = document.createElement("section");
  referenceSection.className = "references";
  const title = document.createElement("h3");
  title.textContent = "参考资料";
  referenceSection.append(title);

  for (const reference of references) {
    const item = referenceTemplate.content.cloneNode(true);
    item.querySelector(".reference-name").textContent = reference.name;
    item.querySelector(".reference-score").textContent = `相关度 ${Math.round(reference.relevance_score * 100)}%`;
    item.querySelector(".reference-source").textContent = `来源：${reference.source || "未标注来源"}`;
    const confidence = item.querySelector(".reference-confidence");
    confidence.textContent = `可信度：${getSourceTierLabel(reference.source_tier)} | 最后更新：${formatUpdatedAt(reference.updated_at)}`;
    if (reference.needs_review) {
      confidence.classList.add("needs-review");
      confidence.textContent += " | 资料需核验，不能作为医疗结论";
    }
    item.querySelector(".reference-excerpt").textContent = reference.excerpt;
    referenceSection.append(item);
  }
  message.append(referenceSection);
}

function appendFeedback(message, role, assistantMessageId) {
  if (role !== "assistant" || !assistantMessageId) return;
  const feedback = document.createElement("div");
  feedback.className = "feedback-controls";
  feedback.innerHTML = `
    <span>这条回答对你有帮助吗？</span>
    <button type="button" data-helpful="true">有帮助</button>
    <button type="button" data-helpful="false">没帮助</button>
    <span class="feedback-status" aria-live="polite"></span>
  `;
  feedback.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      const helpful = button.dataset.helpful === "true";
      submitFeedback(feedback, assistantMessageId, helpful);
    });
  });
  message.append(feedback);
}

function appendTrace(message, trace) {
  const pathLabels = {
    "rag-vector-retrieval": "RAG 检索 + 模型生成",
    "vector-search-no-match": "未找到相关资料",
    "safety-keyword-guard": "安全拦截",
  };
  const traceSection = document.createElement("div");
  traceSection.className = "answer-trace";
  const title = document.createElement("span");
  title.textContent = "本次回答过程";
  const path = document.createElement("span");
  path.textContent = pathLabels[trace.processing_path] || "未知处理路径";
  const retrieved = document.createElement("span");
  retrieved.textContent = `命中 ${trace.retrieved_count || 0} 条资料`;
  const latency = document.createElement("span");
  latency.textContent = `耗时 ${trace.latency_ms || 0} ms`;
  traceSection.append(title, path, retrieved, latency);
  message.append(traceSection);
}

async function submitFeedback(container, assistantMessageId, helpful) {
  let reason = null;
  if (!helpful) {
    reason = window.prompt("可以选填原因，例如：资料不足、回答不准确或表达不清楚。");
    if (reason === null) return;
  }

  const buttons = container.querySelectorAll("button");
  const status = container.querySelector(".feedback-status");
  buttons.forEach((button) => { button.disabled = true; });
  status.textContent = "正在保存...";

  try {
    const response = await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assistant_message_id: assistantMessageId,
        helpful,
        reason: reason?.trim() || null,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "保存反馈失败。");
    status.textContent = helpful ? "已记录：有帮助" : "已记录：没帮助";
  } catch (error) {
    status.textContent = `保存失败：${error.message}`;
    buttons.forEach((button) => { button.disabled = false; });
  }
}

function resetConversation() {
  conversationId = createConversationId();
  saveActiveConversation();
  messageList.innerHTML = "";
  appendMessage("已开始新的对话。你可以继续向我询问健康资料中的内容。", "assistant");
  loadConversationList();
  questionInput.focus();
}

function renderWelcomeMessage() {
  messageList.innerHTML = `
    <div class="welcome-message">
      <p class="message-label">医疗健康助手</p>
      <p>你好，可以根据已有资料向我提问，例如“布洛芬有什么作用？”或“睡眠不足时有哪些通用健康建议？”</p>
    </div>
  `;
}

function renderConversationHistory(conversations) {
  historyList.innerHTML = "";
  if (conversations.length === 0) {
    historyList.innerHTML = '<p class="history-empty">暂无已保存的对话</p>';
    return;
  }

  for (const conversation of conversations) {
    const row = document.createElement("div");
    row.className = "history-item";
    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.textContent = conversation.preview;
    openButton.title = conversation.preview;
    openButton.classList.toggle("active", conversation.conversation_id === conversationId);
    openButton.addEventListener("click", () => loadConversation(conversation.conversation_id));
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-history";
    deleteButton.textContent = "x";
    deleteButton.title = "删除此对话";
    deleteButton.setAttribute("aria-label", "删除此对话");
    deleteButton.addEventListener("click", () => deleteConversation(conversation));
    row.append(openButton, deleteButton);
    historyList.append(row);
  }
}

async function loadConversationList() {
  try {
    const response = await fetch("/conversations");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取对话列表失败。"));
    renderConversationHistory(data);
  } catch (error) {
    historyList.innerHTML = '<p class="history-empty">历史对话暂时无法读取</p>';
  }
}

async function loadConversation(nextConversationId) {
  try {
    const response = await fetch(
      `/conversations/${encodeURIComponent(nextConversationId)}/messages`,
    );
    const messages = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(messages, "读取对话失败。"));
    conversationId = nextConversationId;
    saveActiveConversation();
    messageList.innerHTML = "";
    for (const message of messages) {
      appendMessage(
        message.content,
        message.role === "user" ? "user" : "assistant",
        [],
        message.role === "assistant" ? message.id : null,
      );
    }
    if (messages.length === 0) renderWelcomeMessage();
    loadConversationList();
    setManagerVisible(false);
  } catch (error) {
    appendMessage(`无法加载历史对话：${error.message}`, "assistant");
  }
}

async function deleteConversation(conversation) {
  const confirmed = window.confirm(
    `确定删除这段对话“${conversation.preview}”吗？其中的反馈也会同时删除。`,
  );
  if (!confirmed) return;

  try {
    const response = await fetch(
      `/conversations/${encodeURIComponent(conversation.conversation_id)}/messages`,
      { method: "DELETE" },
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(getErrorMessage(data, "删除对话失败。"));
    }
    if (conversation.conversation_id === conversationId) resetConversation();
    await loadConversationList();
  } catch (error) {
    window.alert(`删除失败：${error.message}`);
  }
}

function showKnowledgeStatus(data) {
  knowledgeStatus.className = "knowledge-status";
  if (data.is_current) {
    knowledgeStatus.textContent = `知识库已就绪：${data.document_count} 份资料，${data.chunk_count} 个切块`;
    return;
  }
  knowledgeStatus.classList.add("outdated");
  knowledgeStatus.textContent = `知识库待重建：${data.document_count} 份资料`;
}

async function loadKnowledgeStatus() {
  try {
    const response = await fetch("/knowledge/status");
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "读取失败");
    showKnowledgeStatus(data);
  } catch (error) {
    knowledgeStatus.className = "knowledge-status error";
    knowledgeStatus.textContent = "知识库状态暂时无法读取";
  }
}

async function rebuildKnowledge() {
  const confirmed = window.confirm(
    "重建会重新为全部资料生成向量，可能消耗 OpenAI Embedding 额度。确定继续吗？",
  );
  if (!confirmed) return;

  rebuildKnowledgeButton.disabled = true;
  rebuildKnowledgeButton.textContent = "正在重建...";
  try {
    const response = await fetch("/knowledge/rebuild", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "重建失败");
    showKnowledgeStatus({
      is_current: true,
      document_count: data.document_count,
      chunk_count: data.chunk_count,
    });
    rebuildKnowledgeButton.textContent = "重建完成";
    await loadKnowledgeVersions();
  } catch (error) {
    knowledgeStatus.className = "knowledge-status error";
    knowledgeStatus.textContent = `重建失败：${error.message}`;
    rebuildKnowledgeButton.textContent = "重试重建";
  } finally {
    rebuildKnowledgeButton.disabled = false;
  }
}

function setManagerVisible(visible) {
  knowledgeManager.classList.toggle("is-hidden", !visible);
  qualityDashboard.classList.add("is-hidden");
  messageList.classList.toggle("is-hidden", visible);
  form.classList.toggle("is-hidden", visible);
  managerToggleButton.textContent = visible ? "返回问答" : "管理资料";
  feedbackDashboardToggle.textContent = "质量面板";
  if (visible) {
    searchInput.focus();
    loadReviewQueue();
    loadKnowledgeVersions();
  }
}

function setFeedbackDashboardVisible(visible) {
  qualityDashboard.classList.toggle("is-hidden", !visible);
  knowledgeManager.classList.add("is-hidden");
  messageList.classList.toggle("is-hidden", visible);
  form.classList.toggle("is-hidden", visible);
  feedbackDashboardToggle.textContent = visible ? "返回问答" : "质量面板";
  managerToggleButton.textContent = "管理资料";
  if (visible) {
    loadFeedbackDashboard();
    loadCustomEvaluationCases();
    loadEvaluationHistory();
  }
}

function getErrorMessage(data, fallback) {
  return data?.detail || fallback;
}

function appendInsight(container, text, count = null) {
  const item = document.createElement("div");
  item.className = "insight-item";
  item.textContent = text;
  if (count !== null) {
    const countElement = document.createElement("span");
    countElement.className = "insight-count";
    countElement.textContent = `${count} 次`;
    item.append(countElement);
  }
  container.append(item);
}

function renderFeedbackDashboard(summary, suggestions, recentItems) {
  feedbackMetrics.innerHTML = "";
  const helpfulRate = summary.helpful_rate === null
    ? "暂无"
    : `${Math.round(summary.helpful_rate * 100)}%`;
  const metrics = [
    ["评价总数", summary.total_count],
    ["有帮助率", helpfulRate],
    ["没帮助", summary.not_helpful_count],
  ];
  for (const [label, value] of metrics) {
    const metric = document.createElement("section");
    metric.className = "metric";
    const metricLabel = document.createElement("p");
    metricLabel.className = "metric-label";
    metricLabel.textContent = label;
    const metricValue = document.createElement("p");
    metricValue.className = "metric-value";
    metricValue.textContent = value;
    metric.append(metricLabel, metricValue);
    feedbackMetrics.append(metric);
  }

  commonReasons.innerHTML = "";
  if (suggestions.common_reasons.length === 0) {
    appendInsight(commonReasons, "暂无“没帮助”反馈原因。");
  } else {
    for (const reason of suggestions.common_reasons) {
      appendInsight(commonReasons, reason.text, reason.count);
    }
  }

  recommendedActions.innerHTML = "";
  for (const action of suggestions.recommended_actions) {
    appendInsight(recommendedActions, action);
  }

  recentFeedbackList.innerHTML = "";
  if (recentItems.length === 0) {
    appendInsight(recentFeedbackList, "暂无“没帮助”回答。可以先在问答后留下评价。 ");
    return;
  }
  for (const feedback of recentItems) {
    const item = document.createElement("article");
    item.className = "recent-feedback-item";
    const question = document.createElement("p");
    question.className = "feedback-question";
    question.textContent = `问题：${feedback.question || "未找到原问题"}`;
    const answer = document.createElement("p");
    answer.textContent = `回答：${feedback.answer}`;
    const reason = document.createElement("p");
    reason.className = "feedback-reason";
    reason.textContent = `原因：${feedback.reason || "未填写"}`;
    item.append(question, answer, reason);
    recentFeedbackList.append(item);
  }
}

async function loadFeedbackDashboard() {
  dashboardStatus.textContent = "正在读取反馈数据...";
  try {
    const [summaryResponse, suggestionsResponse, recentResponse] = await Promise.all([
      fetch("/feedback/summary"),
      fetch("/feedback/improvement-suggestions"),
      fetch("/feedback/recent?helpful=false&limit=10"),
    ]);
    const [summary, suggestions, recentItems] = await Promise.all([
      summaryResponse.json(),
      suggestionsResponse.json(),
      recentResponse.json(),
    ]);
    if (!summaryResponse.ok) throw new Error(getErrorMessage(summary, "读取统计失败。"));
    if (!suggestionsResponse.ok) throw new Error(getErrorMessage(suggestions, "读取建议失败。"));
    if (!recentResponse.ok) throw new Error(getErrorMessage(recentItems, "读取反馈明细失败。"));
    renderFeedbackDashboard(summary, suggestions, recentItems);
    dashboardStatus.textContent = "数据已更新。";
  } catch (error) {
    dashboardStatus.textContent = `读取失败：${error.message}`;
  }
}

function renderRagEvaluation(data) {
  evaluationMetrics.innerHTML = "";
  const metrics = [
    ["通过", `${data.passed_count} / ${data.total_count}`],
    ["命中率", `${Math.round(data.pass_rate * 100)}%`],
    ["默认题", data.preset_count],
    ["自定义题", data.custom_count],
  ];
  for (const [label, value] of metrics) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${label}：${value}`;
    evaluationMetrics.append(metric);
  }
  for (const metricData of data.category_metrics) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${metricData.category}：${metricData.passed_count} / ${metricData.total_count}`;
    evaluationMetrics.append(metric);
  }

  evaluationResults.innerHTML = "";
  for (const result of data.results) {
    const item = document.createElement("article");
    item.className = `evaluation-result ${result.passed ? "passed" : "failed"}`;
    const title = document.createElement("h4");
    title.textContent = result.question;
    const detail = document.createElement("p");
    const expectedType = getKnowledgeTypeLabel(result.expected_type);
    if (result.passed) {
      const matchedName = result.matched_name || result.expected_name;
      const isAlternativeMatch = matchedName !== result.expected_name;
      detail.textContent = isAlternativeMatch
        ? `通过：可接受${expectedType}“${matchedName}”命中第 ${result.expected_rank} 条；主目标是“${result.expected_name}”。`
        : `通过：目标${expectedType}“${matchedName}”命中第 ${result.expected_rank} 条。`;
    } else {
      const topResult = result.top_name
        ? `首位结果是${getKnowledgeTypeLabel(result.top_type)}“${result.top_name}”`
        : "没有检索到结果";
      detail.textContent = `未通过：目标${expectedType}“${result.expected_name}”未进入前 3 条；${topResult}。`;
    }
    item.append(title, detail);
    evaluationResults.append(item);
  }
  renderEvaluationQualityGate(data.quality_gate);
}

function renderEvaluationQualityGate(gate) {
  evaluationQualityGate.innerHTML = "";
  if (!gate) return;

  evaluationQualityGate.className = `evaluation-quality-gate ${gate.status}`;
  const title = document.createElement("strong");
  title.textContent = ({
    baseline: "质量基线",
    stable: "质量检查通过",
    improved: "质量有所提升",
    warning: "发现能力回退",
    attention: "排名需要关注",
    expanded: "测试覆盖已扩展",
  })[gate.status] || "质量检查";
  const message = document.createElement("p");
  message.textContent = gate.message;
  evaluationQualityGate.append(title, message);

  if (gate.regressed_questions.length) {
    const regressions = document.createElement("p");
    regressions.textContent = `回退题：${gate.regressed_questions.join("；")}`;
    evaluationQualityGate.append(regressions);
  }
  if (gate.improved_questions.length) {
    const improvements = document.createElement("p");
    improvements.textContent = `提升题：${gate.improved_questions.join("；")}`;
    evaluationQualityGate.append(improvements);
  }
  if (gate.new_questions.length) {
    const additions = document.createElement("p");
    additions.textContent = `新增题：${gate.new_questions.join("；")}`;
    evaluationQualityGate.append(additions);
  }
  if (gate.rank_regressed_questions.length) {
    const rankRegressions = document.createElement("p");
    rankRegressions.textContent = `排名下降题：${gate.rank_regressed_questions.join("；")}`;
    evaluationQualityGate.append(rankRegressions);
  }
  if (gate.rank_improved_questions.length) {
    const rankImprovements = document.createElement("p");
    rankImprovements.textContent = `排名提升题：${gate.rank_improved_questions.join("；")}`;
    evaluationQualityGate.append(rankImprovements);
  }
}

function getStrategyResultText(result, expectedName) {
  const expectedRank = result.expected_rank;
  if (result.passed) {
    const matchedName = result.matched_name || expectedName;
    return matchedName === expectedName
      ? `命中第 ${expectedRank} 条`
      : `可接受资料“${matchedName}”命中第 ${expectedRank} 条`;
  }
  if (!result.top_name) return "未检索到结果";
  return `未命中，首位为${getKnowledgeTypeLabel(result.top_type)}“${result.top_name}”`;
}

function renderRetrievalComparison(data) {
  comparisonMetrics.innerHTML = "";
  const metrics = [
    ["旧策略", `${data.baseline.passed_count} / ${data.total_count} (${Math.round(data.baseline.pass_rate * 100)}%)`],
    ["新策略", `${data.current.passed_count} / ${data.total_count} (${Math.round(data.current.pass_rate * 100)}%)`],
    ["命中率变化", `${data.pass_rate_delta >= 0 ? "+" : ""}${Math.round(data.pass_rate_delta * 100)}%`],
    ["提升题目", data.improved_count],
    ["回退题目", data.regressed_count],
  ];
  for (const [label, value] of metrics) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${label}：${value}`;
    comparisonMetrics.append(metric);
  }

  comparisonResults.innerHTML = "";
  for (const result of data.results) {
    const item = document.createElement("article");
    item.className = `comparison-result ${result.change}`;
    const title = document.createElement("h5");
    title.textContent = result.question;
    const oldResult = document.createElement("p");
    oldResult.textContent = `旧：${getStrategyResultText(result.baseline, result.expected_name)}`;
    const newResult = document.createElement("p");
    newResult.textContent = `新：${getStrategyResultText(result.current, result.expected_name)}`;
    const change = document.createElement("p");
    change.className = "comparison-change";
    change.textContent = ({ improved: "提升", regressed: "回退", unchanged: "不变" })[result.change];
    item.append(title, oldResult, newResult, change);
    comparisonResults.append(item);
  }
}

function renderRetrievalDiagnosis(data) {
  diagnosisMetrics.innerHTML = "";
  const metrics = [
    ["表现正常", data.healthy_count],
    ["可优化", data.attention_count],
    ["未命中", data.failed_count],
  ];
  for (const [label, value] of metrics) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${label}：${value}`;
    diagnosisMetrics.append(metric);
  }

  diagnosisResults.innerHTML = "";
  for (const result of data.results) {
    const item = document.createElement("article");
    item.className = `diagnosis-result ${result.diagnostic_level}`;
    const title = document.createElement("h5");
    title.textContent = result.question;
    const diagnostic = document.createElement("p");
    diagnostic.textContent = result.diagnostic;
    const action = document.createElement("p");
    action.className = "diagnosis-action";
    action.textContent = `建议：${result.suggested_action}`;
    const candidates = document.createElement("p");
    candidates.className = "diagnosis-candidates";
    candidates.textContent = result.candidates.length
      ? `当前前三条：${result.candidates.map((item) => `${item.rank}. ${getKnowledgeTypeLabel(item.type)}“${item.name}” (${item.relevance_score})`).join("；")}`
      : "当前前三条：没有达到相关度阈值的资料。";
    item.append(title, diagnostic, action, candidates);
    diagnosisResults.append(item);
  }
}

function renderCustomEvaluationCases(data) {
  customEvaluationList.innerHTML = "";
  if (data.cases.length === 0) {
    customEvaluationStatus.textContent = "还没有自定义题。可从你最常问、最希望检索正确的问题开始添加。";
    return;
  }

  customEvaluationStatus.textContent = `已保存 ${data.total_count} 道自定义题，运行全部评测时会一并检查。`;
  for (const item of data.cases) {
    const row = document.createElement("article");
    row.className = "custom-evaluation-item";
    const text = document.createElement("p");
    const alternatives = item.alternative_names.length
      ? `｜可接受：${item.alternative_names.join("、")}`
      : "";
    text.textContent = `问题：${item.question}｜分类：${item.category}｜目标${getKnowledgeTypeLabel(item.expected_type)}：${item.expected_name}${alternatives}`;
    const removeButton = document.createElement("button");
    removeButton.className = "text-button danger-button";
    removeButton.type = "button";
    removeButton.textContent = "删除";
    removeButton.addEventListener("click", () => deleteCustomEvaluationCase(item.id));
    row.append(text, removeButton);
    customEvaluationList.append(row);
  }
}

function formatEvaluationTime(value) {
  return new Date(value).toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderEvaluationHistory(data) {
  evaluationHistoryList.innerHTML = "";
  if (data.runs.length === 0) {
    evaluationHistoryStatus.textContent = "还没有评测历史。运行一次评测后会自动保存。";
    return;
  }

  evaluationHistoryStatus.textContent = `共保存 ${data.total_count} 次评测，显示最近 ${data.runs.length} 次。`;
  for (const run of data.runs) {
    const item = document.createElement("article");
    item.className = "evaluation-history-item";
    const summary = document.createElement("p");
    summary.textContent = `${formatEvaluationTime(run.created_at)}｜通过 ${run.passed_count} / ${run.total_count}｜命中率 ${Math.round(run.pass_rate * 100)}%`;
    const detail = document.createElement("p");
    detail.className = "evaluation-history-detail";
    detail.textContent = `默认题 ${run.preset_count} 道，自定义题 ${run.custom_count} 道，知识库资料 ${run.knowledge_document_count} 条`;
    item.append(summary, detail);
    evaluationHistoryList.append(item);
  }
}

async function loadEvaluationHistory() {
  evaluationHistoryStatus.textContent = "正在读取评测历史...";
  try {
    const response = await fetch("/evaluation/history?limit=10");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取评测历史失败。"));
    renderEvaluationHistory(data);
  } catch (error) {
    evaluationHistoryStatus.textContent = `读取失败：${error.message}`;
  }
}

async function loadCustomEvaluationCases() {
  customEvaluationStatus.textContent = "正在读取自定义评测题...";
  try {
    const response = await fetch("/evaluation/cases");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取自定义评测题失败。"));
    renderCustomEvaluationCases(data);
  } catch (error) {
    customEvaluationStatus.textContent = `读取失败：${error.message}`;
  }
}

async function addCustomEvaluationCase(event) {
  event.preventDefault();
  const payload = {
    question: customEvaluationQuestion.value,
    expected_name: customEvaluationExpectedName.value,
    category: customEvaluationCategory.value,
    alternative_names: [...new Set(
      customEvaluationAlternativeNames.value
        .split(/[，,、]/)
        .map((name) => name.trim())
        .filter(Boolean),
    )],
    expected_type: customEvaluationExpectedType.value,
  };
  customEvaluationStatus.textContent = "正在保存自定义题...";
  try {
    const response = await fetch("/evaluation/cases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "保存自定义题失败。"));
    customEvaluationForm.reset();
    await loadCustomEvaluationCases();
  } catch (error) {
    customEvaluationStatus.textContent = `保存失败：${error.message}`;
  }
}

async function deleteCustomEvaluationCase(caseId) {
  if (!window.confirm("删除这道自定义评测题吗？")) return;
  customEvaluationStatus.textContent = "正在删除自定义题...";
  try {
    const response = await fetch(`/evaluation/cases/${caseId}`, { method: "DELETE" });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(getErrorMessage(data, "删除自定义题失败。"));
    }
    await loadCustomEvaluationCases();
  } catch (error) {
    customEvaluationStatus.textContent = `删除失败：${error.message}`;
  }
}

async function runRagEvaluation() {
  const confirmed = window.confirm(
    "将运行默认题和你保存的自定义题，只调用 Embedding，不生成模型回答，可能消耗少量额度。确定继续吗？",
  );
  if (!confirmed) return;

  runRagEvaluationButton.disabled = true;
  runRagEvaluationButton.textContent = "正在评测...";
  evaluationStatus.className = "evaluation-status";
  evaluationStatus.textContent = "正在检查前 3 条检索结果...";
  evaluationMetrics.innerHTML = "";
  evaluationResults.innerHTML = "";
  evaluationQualityGate.innerHTML = "";
  try {
    const response = await fetch("/evaluation/run", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "评测失败。"));
    renderRagEvaluation(data);
    await loadEvaluationHistory();
    evaluationStatus.textContent = "评测完成。通过表示主目标或可接受的同类型资料进入检索结果前 3 条。";
  } catch (error) {
    evaluationStatus.className = "evaluation-status error";
    evaluationStatus.textContent = `评测失败：${error.message}`;
  } finally {
    runRagEvaluationButton.disabled = false;
    runRagEvaluationButton.textContent = "运行全部评测";
  }
}

async function compareRetrievalStrategies() {
  const confirmed = window.confirm(
    "将用默认题和自定义题分别执行旧、新检索策略，只调用 Embedding，不生成模型回答，可能消耗少量额度。确定继续吗？",
  );
  if (!confirmed) return;

  compareRetrievalButton.disabled = true;
  compareRetrievalButton.textContent = "正在对比...";
  comparisonStatus.className = "comparison-status";
  comparisonStatus.textContent = "正在对比原始前 3 切块与当前检索策略...";
  comparisonMetrics.innerHTML = "";
  comparisonResults.innerHTML = "";
  try {
    const response = await fetch("/evaluation/compare", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "检索对比失败。"));
    renderRetrievalComparison(data);
    comparisonStatus.textContent = "对比完成。新策略按资料去重并过滤低相关结果。";
  } catch (error) {
    comparisonStatus.className = "comparison-status error";
    comparisonStatus.textContent = `对比失败：${error.message}`;
  } finally {
    compareRetrievalButton.disabled = false;
    compareRetrievalButton.textContent = "对比新旧检索";
  }
}

async function diagnoseCurrentRetrieval() {
  const confirmed = window.confirm(
    "将诊断默认题和自定义题的当前检索结果，只调用 Embedding，不生成模型回答，可能消耗少量额度。确定继续吗？",
  );
  if (!confirmed) return;

  diagnoseRetrievalButton.disabled = true;
  diagnoseRetrievalButton.textContent = "正在诊断...";
  diagnosisStatus.className = "diagnosis-status";
  diagnosisStatus.textContent = "正在分析目标资料的候选位置和最终排名...";
  diagnosisMetrics.innerHTML = "";
  diagnosisResults.innerHTML = "";
  try {
    const response = await fetch("/evaluation/diagnose", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "检索诊断失败。"));
    renderRetrievalDiagnosis(data);
    diagnosisStatus.textContent = "诊断完成。可根据每题建议补充资料关键词或内容。";
  } catch (error) {
    diagnosisStatus.className = "diagnosis-status error";
    diagnosisStatus.textContent = `诊断失败：${error.message}`;
  } finally {
    diagnoseRetrievalButton.disabled = false;
    diagnoseRetrievalButton.textContent = "诊断当前检索";
  }
}

function clearSearchResults() {
  searchResults.innerHTML = "";
}

function renderReviewQueue(data) {
  reviewResults.innerHTML = "";
  if (data.results.length === 0) {
    reviewStatus.textContent = "目前没有待核验资料。";
    return;
  }

  reviewStatus.textContent = `共 ${data.total_count} 条资料需要核验或更新。`;
  for (const item of data.results) {
    const result = document.createElement("article");
    result.className = "review-item";
    const header = document.createElement("div");
    header.className = "search-result-header";
    const title = document.createElement("h4");
    title.textContent = item.title;
    const type = document.createElement("span");
    type.className = `type-chip ${item.type}`;
    type.textContent = getKnowledgeTypeLabel(item.type);
    header.append(title, type);

    const metadata = document.createElement("p");
    metadata.textContent = `来源：${item.source || "未标注来源"} | 可信度：${getSourceTierLabel(item.source_tier)} | 更新：${formatUpdatedAt(item.updated_at)}`;
    const reasons = document.createElement("p");
    reasons.className = "review-reasons";
    reasons.textContent = `需处理：${item.review_reasons.join("；")}`;
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "去补充来源";
    editButton.addEventListener("click", () => openEditDialog(item));
    result.append(header, metadata, reasons, editButton);
    reviewResults.append(result);
  }
}

async function loadReviewQueue() {
  reviewStatus.className = "review-status";
  reviewStatus.textContent = "正在读取待核验资料...";
  reviewResults.innerHTML = "";
  refreshReviewQueueButton.disabled = true;
  try {
    const response = await fetch("/knowledge/review-queue");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取待核验资料失败。"));
    renderReviewQueue(data);
  } catch (error) {
    reviewStatus.className = "review-status error";
    reviewStatus.textContent = `读取失败：${error.message}`;
  } finally {
    refreshReviewQueueButton.disabled = false;
  }
}

function renderKnowledgeVersions(data) {
  versionResults.innerHTML = "";
  if (data.versions.length === 0) {
    versionStatus.textContent = "还没有版本记录。下次重建知识库时会自动保存当前资料。";
    return;
  }

  versionStatus.textContent = `已保存 ${data.total_count} 个本地版本。`;
  for (const version of data.versions) {
    const item = document.createElement("article");
    item.className = "version-item";
    if (version.is_current) item.classList.add("current");

    const header = document.createElement("div");
    header.className = "search-result-header";
    const title = document.createElement("h4");
    title.textContent = `版本 #${version.id}`;
    const state = document.createElement("span");
    state.className = "version-state";
    state.textContent = version.is_current ? "当前资料" : "历史版本";
    header.append(title, state);

    const detail = document.createElement("p");
    detail.textContent = `${getSnapshotReasonLabel(version.reason)} | ${version.document_count} 份资料 | 保存于 ${formatUpdatedAt(version.created_at)}`;
    item.append(header, detail);

    if (version.is_current) {
      const currentNote = document.createElement("p");
      currentNote.className = "version-current-note";
      currentNote.textContent = "这就是当前资料状态，无需恢复。";
      item.append(currentNote);
    } else {
      const restoreButton = document.createElement("button");
      restoreButton.type = "button";
      restoreButton.textContent = "恢复此版本";
      restoreButton.addEventListener("click", () => restoreKnowledgeVersion(version, restoreButton));
      item.append(restoreButton);
    }
    versionResults.append(item);
  }
}

async function loadKnowledgeVersions() {
  versionStatus.className = "version-status";
  versionStatus.textContent = "正在读取本地版本...";
  versionResults.innerHTML = "";
  refreshKnowledgeVersionsButton.disabled = true;
  try {
    const response = await fetch("/knowledge/versions");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取版本失败。"));
    renderKnowledgeVersions(data);
  } catch (error) {
    versionStatus.className = "version-status error";
    versionStatus.textContent = `读取失败：${error.message}`;
  } finally {
    refreshKnowledgeVersionsButton.disabled = false;
  }
}

async function restoreKnowledgeVersion(version, button) {
  const confirmed = window.confirm(
    `恢复版本 #${version.id} 会覆盖当前的病症、药物和手写资料。系统会先自动备份当前资料，再重新建立向量库。确定恢复吗？`,
  );
  if (!confirmed) return;

  button.disabled = true;
  button.textContent = "正在恢复...";
  try {
    const response = await fetch(`/knowledge/versions/${version.id}/restore`, {
      method: "POST",
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "恢复失败。"));
    entryStatus.className = "manager-status";
    entryStatus.textContent = `已恢复版本 #${data.restored_version_id}，并自动备份为版本 #${data.backup_version_id}。向量库已重建。`;
    await Promise.all([
      loadKnowledgeStatus(),
      loadReviewQueue(),
      loadKnowledgeVersions(),
    ]);
    if (searchInput.value.trim()) searchForm.requestSubmit();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `恢复失败：${error.message}`;
    button.disabled = false;
    button.textContent = "恢复此版本";
  }
}

function renderSearchResults(data) {
  clearSearchResults();
  if (data.results.length === 0) {
    searchStatus.textContent = `没有找到与“${data.query}”相关的资料。`;
    return;
  }

  searchStatus.textContent = `找到 ${data.total_count} 条资料。`;
  for (const item of data.results) {
    const result = document.createElement("article");
    result.className = "search-result";
    const header = document.createElement("div");
    header.className = "search-result-header";
    const title = document.createElement("h3");
    title.textContent = item.title;
    const type = document.createElement("span");
    type.className = `type-chip ${item.type}`;
    type.textContent = getKnowledgeTypeLabel(item.type);
    header.append(title, type);
    const fields = document.createElement("p");
    const reviewNote = item.needs_review ? " | 需核验" : "";
    fields.textContent = `匹配字段：${item.matched_fields.join("、")} | 来源：${item.source || "未标注来源"} | 可信度：${getSourceTierLabel(item.source_tier)} | 更新：${formatUpdatedAt(item.updated_at)}${reviewNote}`;
    const excerpt = document.createElement("p");
    excerpt.textContent = item.excerpt;
    const actions = document.createElement("div");
    actions.className = "result-actions";
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "编辑";
    editButton.addEventListener("click", () => openEditDialog(item));
    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "删除";
    deleteButton.addEventListener("click", () => deleteKnowledgeEntry(item));
    actions.append(editButton, deleteButton);
    result.append(header, fields, excerpt, actions);
    searchResults.append(result);
  }
}

async function searchKnowledge(event) {
  event.preventDefault();
  const query = searchInput.value.trim();
  if (!query) return;

  searchStatus.className = "manager-status";
  searchStatus.textContent = "正在搜索...";
  clearSearchResults();
  try {
    const response = await fetch(`/knowledge/search?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "搜索失败。"));
    renderSearchResults(data);
  } catch (error) {
    searchStatus.className = "manager-status error";
    searchStatus.textContent = `搜索失败：${error.message}`;
  }
}

async function createKnowledgeEntry(formElement, endpoint) {
  const submitButton = formElement.querySelector("button[type='submit']");
  const payload = Object.fromEntries(new FormData(formElement).entries());
  entryStatus.className = "manager-status";
  entryStatus.textContent = "正在保存资料...";
  submitButton.disabled = true;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "保存失败。"));
    formElement.reset();
    formElement.elements.source.value = "未标注来源";
    formElement.elements.source_tier.value = "unverified";
    entryStatus.textContent = `已保存“${data.name || data.title}”。知识库已变为待重建状态。`;
    await loadKnowledgeStatus();
    await loadReviewQueue();
    await loadKnowledgeVersions();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `保存失败：${error.message}`;
  } finally {
    submitButton.disabled = false;
  }
}

async function uploadKnowledgeFile(event) {
  event.preventDefault();
  const file = uploadFile.files[0];
  if (!file) return;

  const submitButton = uploadForm.querySelector("button[type='submit']");
  const formData = new FormData();
  formData.append("file", file);
  entryStatus.className = "manager-status";
  entryStatus.textContent = `正在上传“${file.name}”...`;
  submitButton.disabled = true;

  try {
    const response = await fetch("/documents/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "上传失败。"));
    uploadForm.reset();
    entryStatus.textContent = `已上传“${data.title}”。知识库已变为待重建状态。`;
    await loadKnowledgeStatus();
    await loadReviewQueue();
    await loadKnowledgeVersions();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `上传失败：${error.message}`;
  } finally {
    submitButton.disabled = false;
  }
}

function closeEditDialog() {
  editDialog.close();
  activeEdit = null;
  editFields.innerHTML = "";
  editStatus.textContent = "";
}

async function openEditDialog(item) {
  const config = entryConfiguration[item.type];
  if (!config) return;

  try {
    const response = await fetch(`${config.endpoint}/${item.record_id}`);
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取资料失败。"));
    activeEdit = { id: item.record_id, type: item.type, config };
    editTitle.textContent = `编辑${config.label}：${data.name || data.title}`;
    editFields.innerHTML = "";
    for (const [name, label, controlType] of config.fields) {
      const fieldLabel = document.createElement("label");
      fieldLabel.textContent = label;
      const control = document.createElement(controlType);
      control.name = name;
      control.required = true;
      if (controlType === "select") {
        for (const [value, optionLabel] of SOURCE_TIER_OPTIONS) {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = optionLabel;
          control.append(option);
        }
      }
      control.value = data[name];
      if (controlType === "textarea") control.rows = name === "content" ? 8 : 4;
      fieldLabel.append(control);
      editFields.append(fieldLabel);
    }
    const metadata = document.createElement("p");
    metadata.className = "edit-metadata";
    metadata.textContent = `最后更新：${formatUpdatedAt(data.updated_at)}${data.updated_at ? "（保存后会刷新）" : "（保存后会补上）"}`;
    editFields.append(metadata);
    editDialog.showModal();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `无法打开编辑：${error.message}`;
  }
}

async function saveEdit(event) {
  event.preventDefault();
  if (!activeEdit) return;
  const saveButton = editForm.querySelector("button[type='submit']");
  const payload = Object.fromEntries(new FormData(editForm).entries());
  saveButton.disabled = true;
  editStatus.className = "manager-status";
  editStatus.textContent = "正在保存修改...";

  try {
    const response = await fetch(
      `${activeEdit.config.endpoint}/${activeEdit.id}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    );
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "保存修改失败。"));
    closeEditDialog();
    entryStatus.className = "manager-status";
    entryStatus.textContent = `已修改“${data.name || data.title}”。知识库已变为待重建状态。`;
    await loadKnowledgeStatus();
    await loadReviewQueue();
    await loadKnowledgeVersions();
    if (searchInput.value.trim()) searchForm.requestSubmit();
  } catch (error) {
    editStatus.className = "manager-status error";
    editStatus.textContent = `保存失败：${error.message}`;
  } finally {
    saveButton.disabled = false;
  }
}

async function deleteKnowledgeEntry(item) {
  const config = entryConfiguration[item.type];
  if (!config) return;
  const confirmed = window.confirm(
    `确定删除${config.label}“${item.title}”吗？删除后无法恢复。`,
  );
  if (!confirmed) return;

  entryStatus.className = "manager-status";
  entryStatus.textContent = `正在删除“${item.title}”...`;
  try {
    const response = await fetch(`${config.endpoint}/${item.record_id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(getErrorMessage(data, "删除失败。"));
    }
    entryStatus.textContent = `已删除“${item.title}”。知识库已变为待重建状态。`;
    await loadKnowledgeStatus();
    await loadReviewQueue();
    await loadKnowledgeVersions();
    if (searchInput.value.trim()) searchForm.requestSubmit();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `删除失败：${error.message}`;
  }
}

async function requestStreamingAnswer(question) {
  const response = await fetch("/ask/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_id: conversationId }),
  });
  if (!response.ok) {
    const data = await response.json();
    throw new Error(getErrorMessage(data, "请求失败，请稍后再试。"));
  }
  if (!response.body) throw new Error("浏览器不支持流式响应。");

  const assistantMessage = appendMessage("", "assistant");
  const answerText = assistantMessage.querySelector(".message-content");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let metadata = { references: [] };
  let completed = false;

  function processEvent(rawEvent) {
    const lines = rawEvent.split("\n");
    const eventLine = lines.find((line) => line.startsWith("event:"));
    const dataLine = lines.find((line) => line.startsWith("data:"));
    if (!eventLine || !dataLine) return;
    const eventName = eventLine.slice(6).trim();
    const data = JSON.parse(dataLine.slice(5).trim());

    if (eventName === "metadata") {
      metadata = data;
    } else if (eventName === "token") {
      answerText.textContent += data.text;
      scrollToLatestMessage();
    } else if (eventName === "done") {
      appendReferences(assistantMessage, metadata.references || []);
      appendTrace(assistantMessage, { ...metadata, ...data });
      appendFeedback(assistantMessage, "assistant", data.assistant_message_id);
      completed = true;
      scrollToLatestMessage();
    } else if (eventName === "error") {
      throw new Error(data.detail || "流式回答中断。");
    }
  }

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r/g, "");
    let separatorIndex = buffer.indexOf("\n\n");
    while (separatorIndex !== -1) {
      const rawEvent = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);
      processEvent(rawEvent);
      separatorIndex = buffer.indexOf("\n\n");
    }
  }

  if (!completed) throw new Error("回答未能完整生成，请重试。");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage(question, "user");
  questionInput.value = "";
  sendButton.disabled = true;
  sendButton.textContent = "正在查询";

  try {
    await requestStreamingAnswer(question);
    loadConversationList();
  } catch (error) {
    appendMessage(`暂时无法回答：${error.message}`, "assistant");
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "发送";
    questionInput.focus();
  }
});

newChatButton.addEventListener("click", resetConversation);
refreshHistoryButton.addEventListener("click", loadConversationList);
rebuildKnowledgeButton.addEventListener("click", rebuildKnowledge);
refreshReviewQueueButton.addEventListener("click", loadReviewQueue);
refreshKnowledgeVersionsButton.addEventListener("click", loadKnowledgeVersions);
runRagEvaluationButton.addEventListener("click", runRagEvaluation);
compareRetrievalButton.addEventListener("click", compareRetrievalStrategies);
diagnoseRetrievalButton.addEventListener("click", diagnoseCurrentRetrieval);
refreshEvaluationHistoryButton.addEventListener("click", loadEvaluationHistory);
customEvaluationForm.addEventListener("submit", addCustomEvaluationCase);
managerToggleButton.addEventListener("click", () => {
  setManagerVisible(knowledgeManager.classList.contains("is-hidden"));
});
feedbackDashboardToggle.addEventListener("click", () => {
  setFeedbackDashboardVisible(qualityDashboard.classList.contains("is-hidden"));
});
refreshFeedbackButton.addEventListener("click", loadFeedbackDashboard);
searchForm.addEventListener("submit", searchKnowledge);
uploadForm.addEventListener("submit", uploadKnowledgeFile);
editForm.addEventListener("submit", saveEdit);
document.querySelector("#edit-cancel").addEventListener("click", closeEditDialog);
document.querySelector("#edit-cancel-bottom").addEventListener("click", closeEditDialog);
document.querySelector("#condition-form").addEventListener("submit", (event) => {
  event.preventDefault();
  createKnowledgeEntry(event.currentTarget, "/conditions");
});
document.querySelector("#drug-form").addEventListener("submit", (event) => {
  event.preventDefault();
  createKnowledgeEntry(event.currentTarget, "/drugs");
});
document.querySelector("#document-form").addEventListener("submit", (event) => {
  event.preventDefault();
  createKnowledgeEntry(event.currentTarget, "/documents");
});
loadKnowledgeStatus();
saveActiveConversation();
loadConversationList();
loadConversation(conversationId);

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
