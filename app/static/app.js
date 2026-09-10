const form = document.querySelector("#ask-form");
const questionInput = document.querySelector("#question");
const retrievalScopeSelect = document.querySelector("#retrieval-scope");
const sourceFilterSelect = document.querySelector("#source-filter");
const messageList = document.querySelector("#message-list");
const sendButton = document.querySelector("#send-button");
const newChatButton = document.querySelector("#new-chat");
const exportConversationButton = document.querySelector("#export-conversation");
const accountToggleButton = document.querySelector("#account-toggle");
const accountLabel = document.querySelector("#account-label");
const accountDialog = document.querySelector("#account-dialog");
const accountDialogCloseButton = document.querySelector("#account-dialog-close");
const accountLoggedOut = document.querySelector("#account-logged-out");
const accountLoggedIn = document.querySelector("#account-logged-in");
const accountForm = document.querySelector("#account-form");
const accountInput = document.querySelector("#account-input");
const accountPasswordInput = document.querySelector("#account-password");
const accountConfirmField = document.querySelector("#account-confirm-field");
const accountConfirmPasswordInput = document.querySelector("#account-confirm-password");
const accountSubmitButton = document.querySelector("#account-submit");
const accountStatus = document.querySelector("#account-status");
const accountCurrent = document.querySelector("#account-current");
const accountLogoutButton = document.querySelector("#account-logout");
const accountLoggedInStatus = document.querySelector("#account-logged-in-status");
const refreshMemoryButton = document.querySelector("#refresh-memory");
const memoryStats = document.querySelector("#memory-stats");
const memorySummary = document.querySelector("#memory-summary");
const memoryRecentList = document.querySelector("#memory-recent-list");
const memoryLongTermList = document.querySelector("#memory-long-term-list");
const memoryStatus = document.querySelector("#memory-status");
const referenceTemplate = document.querySelector("#reference-template");
const referenceDialog = document.querySelector("#reference-dialog");
const referenceDialogTitle = document.querySelector("#reference-dialog-title");
const referenceDetails = document.querySelector("#reference-details");
const referenceDialogStatus = document.querySelector("#reference-dialog-status");
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
const webImportForm = document.querySelector("#web-import-form");
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
const refreshMonitoringButton = document.querySelector("#refresh-monitoring");
const monitoringWindow = document.querySelector("#monitoring-window");
const monitoringStatus = document.querySelector("#monitoring-status");
const monitoringMetrics = document.querySelector("#monitoring-metrics");
const monitoringPathList = document.querySelector("#monitoring-path-list");
const monitoringFailureList = document.querySelector("#monitoring-failure-list");
const commonReasons = document.querySelector("#common-reasons");
const recommendedActions = document.querySelector("#recommended-actions");
const recentFeedbackList = document.querySelector("#recent-feedback-list");
const reviewStatus = document.querySelector("#review-status");
const reviewResults = document.querySelector("#review-results");
const refreshReviewQueueButton = document.querySelector("#refresh-review-queue");
const reviewBatchForm = document.querySelector("#review-batch-form");
const reviewBatchSubmitButton = document.querySelector("#review-batch-submit");
const reviewBatchStatus = document.querySelector("#review-batch-status");
const reviewHistoryStatus = document.querySelector("#review-history-status");
const reviewHistoryResults = document.querySelector("#review-history-results");
const refreshReviewHistoryButton = document.querySelector("#refresh-review-history");
const versionStatus = document.querySelector("#version-status");
const versionResults = document.querySelector("#version-results");
const refreshKnowledgeVersionsButton = document.querySelector("#refresh-knowledge-versions");
const rebuildHistoryStatus = document.querySelector("#rebuild-history-status");
const rebuildHistoryResults = document.querySelector("#rebuild-history-results");
const refreshRebuildHistoryButton = document.querySelector("#refresh-rebuild-history");
const runRagEvaluationButton = document.querySelector("#run-rag-evaluation");
const runQualityEvaluationButton = document.querySelector("#run-quality-evaluation");
const runRagasEvaluationButton = document.querySelector("#run-ragas-evaluation");
const evaluationRetrievalStrategy = document.querySelector("#evaluation-retrieval-strategy");
const ragasSampleSize = document.querySelector("#ragas-sample-size");
const comparisonBaselineStrategy = document.querySelector("#comparison-baseline-strategy");
const compareRetrievalButton = document.querySelector("#compare-retrieval");
const diagnoseRetrievalButton = document.querySelector("#diagnose-retrieval");
const evaluationStatus = document.querySelector("#evaluation-status");
const evaluationMetrics = document.querySelector("#evaluation-metrics");
const evaluationResults = document.querySelector("#evaluation-results");
const evaluationResultsDetails = document.querySelector("#evaluation-results-details");
const evaluationResultsSummary = document.querySelector("#evaluation-results-summary");
const evaluationQualityGate = document.querySelector("#evaluation-quality-gate");
const ragasEvaluationStatus = document.querySelector("#ragas-evaluation-status");
const ragasEvaluationMetrics = document.querySelector("#ragas-evaluation-metrics");
const ragasEvaluationResults = document.querySelector("#ragas-evaluation-results");
const ragasEvaluationResultsDetails = document.querySelector("#ragas-evaluation-results-details");
const ragasEvaluationResultsSummary = document.querySelector("#ragas-evaluation-results-summary");
const qualityEvaluationStatus = document.querySelector("#quality-evaluation-status");
const qualityEvaluationMetrics = document.querySelector("#quality-evaluation-metrics");
const qualityEvaluationResults = document.querySelector("#quality-evaluation-results");
const qualityEvaluationResultsDetails = document.querySelector("#quality-evaluation-results-details");
const qualityEvaluationResultsSummary = document.querySelector("#quality-evaluation-results-summary");
const refreshEvaluationHistoryButton = document.querySelector("#refresh-evaluation-history");
const evaluationHistoryStatus = document.querySelector("#evaluation-history-status");
const evaluationHistoryList = document.querySelector("#evaluation-history-list");
const customEvaluationForm = document.querySelector("#custom-evaluation-form");
const customEvaluationQuestion = document.querySelector("#evaluation-question");
const customEvaluationExpectedName = document.querySelector("#evaluation-expected-name");
const customEvaluationAlternativeNames = document.querySelector("#evaluation-alternative-names");
const customEvaluationAnswerKeywords = document.querySelector("#evaluation-answer-keywords");
const customEvaluationCitationNames = document.querySelector("#evaluation-citation-names");
const customEvaluationExpectedRefusal = document.querySelector("#evaluation-expected-refusal");
const customEvaluationCategory = document.querySelector("#evaluation-category");
const customEvaluationExpectedType = document.querySelector("#evaluation-expected-type");
const customEvaluationStatus = document.querySelector("#custom-evaluation-status");
const customEvaluationList = document.querySelector("#custom-evaluation-list");
const customEvaluationDetails = document.querySelector("#custom-evaluation-details");
const customEvaluationSummary = document.querySelector("#custom-evaluation-summary");
const comparisonStatus = document.querySelector("#comparison-status");
const comparisonMetrics = document.querySelector("#comparison-metrics");
const comparisonResults = document.querySelector("#comparison-results");
const comparisonResultsDetails = document.querySelector("#comparison-results-details");
const comparisonResultsSummary = document.querySelector("#comparison-results-summary");
const diagnosisStatus = document.querySelector("#diagnosis-status");
const diagnosisMetrics = document.querySelector("#diagnosis-metrics");
const diagnosisResults = document.querySelector("#diagnosis-results");
const diagnosisResultsDetails = document.querySelector("#diagnosis-results-details");
const diagnosisResultsSummary = document.querySelector("#diagnosis-results-summary");

let rebuildPolling = false;
let ragasEvaluationPollingTimer = null;

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
      ["source_url", "来源链接（可选）", "input", "url"],
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
      ["source_url", "来源链接（可选）", "input", "url"],
      ["source_tier", "可信度等级", "select"],
    ],
  },
  document: {
    endpoint: "/documents",
    label: "资料",
    fields: [
      ["title", "资料标题", "input"],
      ["source", "资料来源", "input"],
      ["source_url", "来源链接（可选）", "input", "url"],
      ["source_tier", "可信度等级", "select"],
      ["content", "资料内容", "textarea"],
    ],
  },
};

let activeEdit = null;
const selectedReviewTargets = new Map();

const ACTIVE_CONVERSATION_KEY = "medical-health-active-conversation";
const AUTH_TOKEN_KEY = "medical-health-auth-token";
const nativeFetch = window.fetch.bind(window);
let accountMode = "login";
let currentUser = null;
let conversationId = localStorage.getItem(ACTIVE_CONVERSATION_KEY) || createConversationId();

function createConversationId() {
  return `web-${crypto.randomUUID()}`;
}

function saveActiveConversation() {
  localStorage.setItem(ACTIVE_CONVERSATION_KEY, conversationId);
}

function apiFetch(input, init = {}) {
  const headers = new Headers(init.headers || {});
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  return nativeFetch(input, { ...init, headers });
}

function saveAuthSession(data) {
  localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
  currentUser = data.user;
  renderAccountState();
  refreshAuthenticatedView();
}

function clearAuthSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  currentUser = null;
  renderAccountState();
  renderWelcomeMessage();
  historyList.innerHTML = '<p class="history-empty">登录后查看历史对话</p>';
}

function setAccountMode(mode) {
  accountMode = mode;
  const isRegister = mode === "register";
  document.querySelectorAll("[data-account-mode]").forEach((tab) => {
    const isActive = tab.dataset.accountMode === mode;
    tab.classList.toggle("active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
  });
  accountConfirmField.classList.toggle("is-hidden", !isRegister);
  accountConfirmPasswordInput.required = isRegister;
  accountPasswordInput.autocomplete = isRegister ? "new-password" : "current-password";
  accountSubmitButton.textContent = isRegister ? "注册并登录" : "登录";
  accountStatus.textContent = "";
  accountStatus.className = "account-status";
}

function renderAccountState() {
  const loggedIn = Boolean(currentUser);
  accountLoggedOut.classList.toggle("is-hidden", loggedIn);
  accountLoggedIn.classList.toggle("is-hidden", !loggedIn);
  accountLabel.textContent = "我的";
  accountToggleButton.title = loggedIn
    ? `我的账号：${currentUser.account}`
    : "打开我的账号";
  accountToggleButton.setAttribute("aria-label", accountToggleButton.title);
  if (loggedIn) accountCurrent.textContent = currentUser.account;
  updatePermissionUI();
}

function getMemoryKeyLabel(memoryKey) {
  return ({
    user_name: "称呼",
    user_age: "年龄",
    preferred_language: "语言偏好",
    preferred_style: "回答风格",
    allergy: "过敏史",
    medical_history: "病史",
    long_term_medication: "长期用药",
  })[memoryKey] || "用户信息";
}

function createMemoryStat(label, value) {
  const item = document.createElement("div");
  item.className = "memory-stat";
  const labelElement = document.createElement("span");
  labelElement.textContent = label;
  const valueElement = document.createElement("strong");
  valueElement.textContent = value;
  item.append(labelElement, valueElement);
  return item;
}

function renderMemoryOverview(data) {
  memoryStats.innerHTML = "";
  memoryStats.append(
    createMemoryStat("短期消息", `${data.short_term_message_count}/${data.recent_message_limit}`),
    createMemoryStat("已压缩消息", String(data.summarized_message_count)),
    createMemoryStat("长期记忆", String(data.long_term_memories.length)),
  );

  memorySummary.textContent = data.short_term_summary || "当前会话还没有摘要。对话超过一定长度后，旧内容会自动压缩到这里。";

  memoryRecentList.innerHTML = "";
  if (data.recent_messages?.length) {
    for (const message of data.recent_messages) {
      const item = document.createElement("p");
      item.className = "memory-recent-item";
      item.textContent = `${message.role === "user" ? "你" : "助手"}：${message.content}`;
      memoryRecentList.append(item);
    }
  } else {
    memoryRecentList.innerHTML = '<p class="memory-empty">当前会话还没有消息。</p>';
  }

  memoryLongTermList.innerHTML = "";
  if (data.long_term_memories.length === 0) {
    memoryLongTermList.innerHTML = '<p class="memory-empty">还没有保存长期记忆。你可以在对话中明确说“我叫……”或“我对……过敏”。</p>';
    return;
  }
  for (const memory of data.long_term_memories) {
    const item = document.createElement("article");
    item.className = "memory-long-term-item";
    const content = document.createElement("div");
    const heading = document.createElement("strong");
    heading.textContent = getMemoryKeyLabel(memory.memory_key);
    const text = document.createElement("p");
    text.textContent = memory.content;
    const meta = document.createElement("small");
    meta.textContent = `重要性 ${Math.round(memory.importance * 100)}% | 使用 ${memory.access_count} 次`;
    content.append(heading, text, meta);
    const deleteButton = document.createElement("button");
    deleteButton.className = "text-button danger-button";
    deleteButton.type = "button";
    deleteButton.textContent = "删除";
    deleteButton.title = "删除这条长期记忆";
    deleteButton.addEventListener("click", () => deleteUserMemory(memory, deleteButton));
    item.append(content, deleteButton);
    memoryLongTermList.append(item);
  }
}

async function loadMemoryOverview() {
  if (!currentUser) return;
  memoryStatus.className = "memory-status account-status";
  memoryStatus.textContent = "正在读取记忆...";
  refreshMemoryButton.disabled = true;
  try {
    const response = await apiFetch(`/memory?conversation_id=${encodeURIComponent(conversationId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取记忆失败。"));
    renderMemoryOverview(data);
    memoryStatus.textContent = `已读取会话 ${conversationId}`;
  } catch (error) {
    memoryStatus.className = "memory-status account-status error";
    memoryStatus.textContent = `读取失败：${error.message}`;
  } finally {
    refreshMemoryButton.disabled = false;
  }
}

async function deleteUserMemory(memory, button) {
  if (!window.confirm(`确定删除这条长期记忆吗？\n${memory.content}`)) return;
  button.disabled = true;
  memoryStatus.textContent = "正在删除...";
  try {
    const response = await apiFetch(`/memory/${memory.id}`, { method: "DELETE" });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "删除记忆失败。"));
    await loadMemoryOverview();
    memoryStatus.textContent = "已删除这条长期记忆。";
  } catch (error) {
    memoryStatus.className = "memory-status account-status error";
    memoryStatus.textContent = `删除失败：${error.message}`;
    button.disabled = false;
  }
}

function updatePermissionUI() {
  const isAdmin = Boolean(currentUser?.is_admin);
  const lock = " \uD83D\uDD12";
  managerToggleButton.textContent = isAdmin ? "管理资料" : `管理资料${lock}`;
  feedbackDashboardToggle.textContent = isAdmin ? "质量面板" : `质量面板${lock}`;
  rebuildKnowledgeButton.textContent = isAdmin ? "重建知识库" : `重建知识库${lock}`;
  const title = isAdmin ? "" : currentUser ? "需要管理员权限" : "请先登录";
  [managerToggleButton, feedbackDashboardToggle, rebuildKnowledgeButton].forEach((button) => {
    button.title = title;
  });
}

function requireLoginForKnowledge() {
  if (currentUser) return true;
  openAccountDialog();
  accountStatus.className = "account-status error";
  accountStatus.textContent = "请先登录后再使用健康知识库。";
  return false;
}

function requireAdminForManagement() {
  if (!requireLoginForKnowledge()) return false;
  if (currentUser.is_admin) return true;
  window.alert("需要管理员权限，普通用户只能查询健康资料。\n请联系管理员处理账号权限。");
  return false;
}

function refreshAuthenticatedView() {
  loadKnowledgeStatus();
  loadConversationList();
}

function openAccountDialog() {
  renderAccountState();
  accountStatus.textContent = "";
  accountLoggedInStatus.textContent = "";
  if (!accountDialog.open) accountDialog.showModal();
  if (currentUser) loadMemoryOverview();
}

function closeAccountDialog() {
  accountDialog.close();
  accountForm.reset();
  accountStatus.textContent = "";
  accountLoggedInStatus.textContent = "";
  setAccountMode("login");
}

async function submitAccount(event) {
  event.preventDefault();
  const payload = {
    account: accountInput.value,
    password: accountPasswordInput.value,
  };
  if (accountMode === "register") {
    payload.confirm_password = accountConfirmPasswordInput.value;
  }

  accountSubmitButton.disabled = true;
  accountStatus.className = "account-status";
  accountStatus.textContent = accountMode === "register" ? "正在注册..." : "正在登录...";
  try {
    const endpoint = accountMode === "register" ? "/auth/register" : "/auth/login";
    const response = await nativeFetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "账号操作失败。"));
    saveAuthSession(data);
    accountForm.reset();
    accountLoggedInStatus.textContent = accountMode === "register" ? "注册成功，已自动登录。" : "登录成功。";
  } catch (error) {
    accountStatus.className = "account-status error";
    accountStatus.textContent = error.message;
  } finally {
    accountSubmitButton.disabled = false;
  }
}

async function logoutAccount() {
  accountLogoutButton.disabled = true;
  accountLoggedInStatus.className = "account-status";
  accountLoggedInStatus.textContent = "正在退出...";
  try {
    const response = await apiFetch("/auth/logout", { method: "POST" });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(getErrorMessage(data, "退出登录失败。"));
    }
    clearAuthSession();
    setAccountMode("login");
    accountStatus.textContent = "已退出登录。";
  } catch (error) {
    accountLoggedInStatus.className = "account-status error";
    accountLoggedInStatus.textContent = error.message;
  } finally {
    accountLogoutButton.disabled = false;
  }
}

async function loadCurrentUser() {
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    renderAccountState();
    return;
  }
  try {
    const response = await apiFetch("/auth/me");
    if (!response.ok) {
      clearAuthSession();
      return;
    }
    currentUser = await response.json();
    renderAccountState();
    refreshAuthenticatedView();
  } catch (_error) {
    clearAuthSession();
  }
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

function isHttpSourceUrl(sourceUrl) {
  try {
    const parsed = new URL(sourceUrl);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch (_error) {
    return false;
  }
}

function createSourceUrlLink(sourceUrl, label = "打开来源链接") {
  if (!sourceUrl || !isHttpSourceUrl(sourceUrl)) return null;
  const link = document.createElement("a");
  link.className = "source-url-link";
  link.href = sourceUrl;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = label;
  return link;
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
  const referenceSection = document.createElement("details");
  referenceSection.className = "references";
  referenceSection.open = false;
  const title = document.createElement("summary");
  title.textContent = `参考资料（${references.length} 条）`;
  referenceSection.append(title);

  for (const reference of references) {
    const item = referenceTemplate.content.cloneNode(true);
    item.querySelector(".reference-name").textContent = reference.name;
    const methodLabels = {
      hybrid: "关键词 + 向量",
      keyword: "关键词",
      vector: "向量",
    };
    const rerankScore = reference.rerank_score ?? reference.relevance_score;
    item.querySelector(".reference-score").textContent =
      `重排相关度 ${Math.round(rerankScore * 100)}% | ${methodLabels[reference.retrieval_method] || "检索"}`;
    const source = item.querySelector(".reference-source");
    source.textContent = `来源：${reference.source || "未标注来源"}`;
    const sourceUrlLink = createSourceUrlLink(reference.source_url);
    if (sourceUrlLink) source.after(sourceUrlLink);
    item.querySelector(".reference-location").textContent =
      `引用位置：${reference.location || (reference.page_number ? `第 ${reference.page_number} 页` : "全文")}`;
    const confidence = item.querySelector(".reference-confidence");
    confidence.textContent = `可信度：${getSourceTierLabel(reference.source_tier)} | 最后更新：${formatUpdatedAt(reference.updated_at)}`;
    if (reference.needs_review) {
      confidence.classList.add("needs-review");
      confidence.textContent += " | 资料需核验，不能作为医疗结论";
    }
    item.querySelector(".reference-excerpt").textContent =
      `引用片段：${reference.excerpt}`;
    const viewButton = item.querySelector(".reference-open");
    if (Number.isInteger(reference.record_id)) {
      viewButton.addEventListener("click", async () => {
        viewButton.disabled = true;
        viewButton.textContent = "正在读取...";
        try {
          await openReferenceDialog(reference);
          viewButton.textContent = "查看原文";
        } catch (error) {
          viewButton.textContent = "读取失败";
          setTimeout(() => { viewButton.textContent = "查看原文"; }, 1600);
        } finally {
          viewButton.disabled = false;
        }
      });
    } else {
      viewButton.remove();
    }
    referenceSection.append(item);
  }
  message.append(referenceSection);
}

function closeReferenceDialog() {
  referenceDialog.close();
  referenceDetails.innerHTML = "";
  referenceDialogStatus.textContent = "";
}

function appendReferenceDetail(label, value) {
  const item = document.createElement("div");
  item.className = "reference-detail";
  const heading = document.createElement("h3");
  heading.textContent = label;
  const content = document.createElement("p");
  content.textContent = value || "未记录";
  item.append(heading, content);
  referenceDetails.append(item);
}

function appendReferenceLinkDetail(label, sourceUrl) {
  const link = createSourceUrlLink(sourceUrl, sourceUrl);
  if (!link) return;
  const item = document.createElement("div");
  item.className = "reference-detail";
  const heading = document.createElement("h3");
  heading.textContent = label;
  item.append(heading, link);
  referenceDetails.append(item);
}

async function openReferenceDialog(reference) {
  const config = entryConfiguration[reference.type];
  if (!config || !Number.isInteger(reference.record_id)) {
    throw new Error("该引用没有可查看的原始资料。");
  }

  const [response, knowledgeStatusData] = await Promise.all([
    apiFetch(`${config.endpoint}/${reference.record_id}`),
    getKnowledgeStatusData().catch(() => null),
  ]);
  const data = await response.json();
  if (!response.ok) throw new Error(getErrorMessage(data, "读取资料失败。"));

  referenceDialogTitle.textContent = data.name || data.title;
  referenceDetails.innerHTML = "";
  appendReferenceDetail("资料类型", getKnowledgeTypeLabel(reference.type));
  appendReferenceDetail("资料来源", data.source);
  appendReferenceLinkDetail("来源链接", data.source_url);
  appendReferenceDetail("来源类型", reference.source_kind || "知识文档");
  appendReferenceDetail(
    "引用位置",
    reference.location || (reference.page_number ? `第 ${reference.page_number} 页` : "全文"),
  );
  appendReferenceDetail("引用标识", reference.citation);
  appendReferenceDetail("引用片段", reference.excerpt);
  appendReferenceDetail("可信度等级", getSourceTierLabel(data.source_tier));
  appendReferenceDetail("最后更新", formatUpdatedAt(data.updated_at));
  if (knowledgeStatusData?.is_current) {
    appendReferenceDetail(
      "向量库状态",
      `已同步到当前知识库，上次建立索引：${formatUpdatedAt(knowledgeStatusData.indexed_at)}`,
    );
  } else if (knowledgeStatusData) {
    appendReferenceDetail(
      "向量库状态",
      "待重建。当前原文可能已经更新，本次回答引用的可能是上次建立索引时的旧版本。",
    );
  } else {
    appendReferenceDetail("向量库状态", "暂时无法确认同步状态。");
  }

  if (reference.type === "condition") {
    appendReferenceDetail("常见症状", data.symptoms);
    appendReferenceDetail("通用处理建议", data.treatment);
  } else if (reference.type === "drug") {
    appendReferenceDetail("药物作用", data.effects);
    appendReferenceDetail("使用说明", data.instructions);
  } else if (reference.type === "document") {
    appendReferenceDetail("资料内容", data.content);
  }

  const warnings = [];
  if (knowledgeStatusData && !knowledgeStatusData.is_current) {
    warnings.push("知识库待重建，当前原文可能尚未被问答使用。");
  }
  if (reference.needs_review) {
    warnings.push("该资料仍需核验，不能作为医疗结论。");
  }
  if (warnings.length > 0) {
    referenceDialogStatus.className = "manager-status warning";
    referenceDialogStatus.textContent = warnings.join(" ");
  } else {
    referenceDialogStatus.className = "manager-status";
    referenceDialogStatus.textContent = "";
  }
  referenceDialog.showModal();
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
    "rag-hybrid-retrieval": "混合检索（关键词 + 向量）+ 模型生成",
    "rag-keyword-retrieval": "关键词检索 + 模型生成",
    "rag-vector-rerank": "向量检索 + rerank 重排序 + 模型生成",
    "rag-hybrid-rerank": "混合检索 + rerank 重排序 + 模型生成",
    "rag-keyword-rerank": "关键词检索 + rerank 重排序 + 模型生成",
    "vector-search-no-match": "未找到相关资料",
    "safety-keyword-guard": "安全拦截",
  };
  const scopeLabels = {
    all: "全部资料",
    condition: "仅病症",
    drug: "仅药物",
    document: "仅健康资料",
  };
  const sourceFilterLabels = {
    all: "全部可信度",
    reviewed: "仅已核验",
  };
  const traceSection = document.createElement("div");
  traceSection.className = "answer-trace";
  const title = document.createElement("span");
  title.textContent = "本次回答过程";
  const path = document.createElement("span");
  path.textContent = pathLabels[trace.processing_path] || "未知处理路径";
  const scope = document.createElement("span");
  scope.textContent = `范围：${scopeLabels[trace.retrieval_scope] || "全部资料"}`;
  const sourceFilter = document.createElement("span");
  sourceFilter.textContent = `可信度：${sourceFilterLabels[trace.source_filter] || "全部可信度"}`;
  const retrieved = document.createElement("span");
  retrieved.textContent = `命中 ${trace.retrieved_count || 0} 条资料`;
  const latency = document.createElement("span");
  latency.textContent = `耗时 ${trace.latency_ms || 0} ms`;
  traceSection.append(title, path, scope, sourceFilter, retrieved, latency);
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
    const response = await apiFetch("/feedback", {
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
  loadMemoryOverview();
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
    const response = await apiFetch("/conversations");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取对话列表失败。"));
    renderConversationHistory(data);
  } catch (error) {
    historyList.innerHTML = '<p class="history-empty">历史对话暂时无法读取</p>';
  }
}

async function loadConversation(nextConversationId) {
  try {
    const response = await apiFetch(
      `/conversations/${encodeURIComponent(nextConversationId)}/messages`,
    );
    const messages = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(messages, "读取对话失败。"));
    conversationId = nextConversationId;
    saveActiveConversation();
    messageList.innerHTML = "";
    for (const message of messages) {
      const metadata = message.response_metadata || {};
      const messageElement = appendMessage(
        message.content,
        message.role === "user" ? "user" : "assistant",
        message.role === "assistant" ? metadata.references || [] : [],
        message.role === "assistant" ? message.id : null,
      );
      if (message.role === "assistant" && metadata.processing_path) {
        appendTrace(messageElement, metadata);
      }
    }
    if (messages.length === 0) renderWelcomeMessage();
    loadConversationList();
    loadMemoryOverview();
    setManagerVisible(false);
  } catch (error) {
    appendMessage(`无法加载历史对话：${error.message}`, "assistant");
  }
}

async function exportConversation() {
  exportConversationButton.disabled = true;
  exportConversationButton.textContent = "正在导出";
  try {
    const response = await apiFetch(
      `/conversations/${encodeURIComponent(conversationId)}/export`,
    );
    if (!response.ok) {
      const data = await response.json();
      throw new Error(getErrorMessage(data, "当前对话还没有可以导出的记录。"));
    }
    const file = await response.blob();
    const url = URL.createObjectURL(file);
    const link = document.createElement("a");
    link.href = url;
    link.download = "medical-health-conversation.md";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    window.alert(`导出失败：${error.message}`);
  } finally {
    exportConversationButton.disabled = false;
    exportConversationButton.textContent = "导出对话";
  }
}

async function deleteConversation(conversation) {
  const confirmed = window.confirm(
    `确定删除这段对话“${conversation.preview}”吗？其中的反馈也会同时删除。`,
  );
  if (!confirmed) return;

  try {
    const response = await apiFetch(
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
  const processingSummary = data.text_cleaning_version && data.chunking_strategy
    ? `文本清洗：${data.text_cleaning_version}；分块：${data.chunking_strategy}，${data.chunk_size} 字符，重叠 ${data.chunk_overlap} 字符`
    : "";
  knowledgeStatus.title = processingSummary || "知识库状态";
  if (data.is_current) {
    knowledgeStatus.textContent = `知识库已就绪：${data.document_count} 份资料，${data.chunk_count} 个切块`;
    return;
  }
  knowledgeStatus.classList.add("outdated");
  knowledgeStatus.textContent = `知识库待重建：${data.document_count} 份资料`;
}

async function loadKnowledgeStatus() {
  try {
    const activeJob = await getActiveRebuildJob();
    if (activeJob) {
      showRebuildJob(activeJob);
      await watchRebuildJob(activeJob.id);
      return;
    }
    showKnowledgeStatus(await getKnowledgeStatusData());
  } catch (error) {
    knowledgeStatus.className = "knowledge-status error";
    knowledgeStatus.textContent = "知识库状态暂时无法读取";
  }
}

async function getKnowledgeStatusData() {
  const response = await apiFetch("/knowledge/status");
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "读取失败");
  return data;
}

async function getActiveRebuildJob() {
  const response = await apiFetch("/knowledge/rebuild/jobs/active");
  const data = await response.json();
  if (!response.ok) throw new Error(getErrorMessage(data, "读取重建任务失败"));
  return data;
}

async function getRebuildJob(jobId) {
  const response = await apiFetch(`/knowledge/rebuild/jobs/${jobId}`);
  const data = await response.json();
  if (!response.ok) throw new Error(getErrorMessage(data, "读取重建任务失败"));
  return data;
}

function showRebuildJob(job) {
  const statusLabel = getRebuildStatusLabel(job.status);
  knowledgeStatus.className = "knowledge-status";
  if (job.status === "failed") knowledgeStatus.classList.add("error");
  if (job.status === "pending" || job.status === "running") {
    knowledgeStatus.classList.add("outdated");
  }
  knowledgeStatus.textContent = `任务 #${job.id}：${statusLabel}`;
  if (job.status === "completed") {
    knowledgeStatus.textContent += `，${job.document_count} 份资料，${job.chunk_count} 个切块`;
  }
  if (job.status === "failed" && job.error_message) {
    knowledgeStatus.textContent += `：${job.error_message}`;
  }
}

function getRebuildStatusLabel(status) {
  return ({
    pending: "等待开始",
    running: "正在生成向量",
    completed: "重建完成",
    failed: "重建失败",
  })[status] || status;
}

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function watchRebuildJob(jobId) {
  if (rebuildPolling) return;
  rebuildPolling = true;
  rebuildKnowledgeButton.disabled = true;
  try {
    while (true) {
      const job = await getRebuildJob(jobId);
      showRebuildJob(job);
      if (job.status === "completed") {
        await loadKnowledgeStatus();
        await loadKnowledgeVersions();
        await loadRebuildJobHistory();
        return;
      }
      if (job.status === "failed") {
        throw new Error(job.error_message || "后台重建失败");
      }
      await wait(1000);
    }
  } finally {
    rebuildPolling = false;
    rebuildKnowledgeButton.disabled = false;
    rebuildKnowledgeButton.textContent = "重建知识库";
  }
}

async function rebuildKnowledge() {
  const confirmed = window.confirm(
    "重建会重新为全部资料生成向量，可能消耗 OpenAI Embedding 额度。确定继续吗？",
  );
  if (!confirmed) return;

  rebuildKnowledgeButton.disabled = true;
  rebuildKnowledgeButton.textContent = "正在提交任务...";
  try {
    const response = await apiFetch("/knowledge/rebuild/async", { method: "POST" });
    const data = await response.json();
    if (!response.ok) {
      if (response.status === 409) {
        const activeJob = await getActiveRebuildJob();
        if (activeJob) {
          await watchRebuildJob(activeJob.id);
          return;
        }
      }
      throw new Error(data.detail || "重建失败");
    }
    await watchRebuildJob(data.id);
  } catch (error) {
    knowledgeStatus.className = "knowledge-status error";
    knowledgeStatus.textContent = `重建失败：${error.message}`;
    rebuildKnowledgeButton.disabled = false;
    rebuildKnowledgeButton.textContent = "重试重建";
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
    loadReviewHistory();
    loadKnowledgeVersions();
    loadRebuildJobHistory();
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
    loadMonitoring();
    loadCustomEvaluationCases();
    loadEvaluationHistory();
    loadLatestRagasEvaluation();
  } else if (ragasEvaluationPollingTimer) {
    window.clearTimeout(ragasEvaluationPollingTimer);
    ragasEvaluationPollingTimer = null;
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
      apiFetch("/feedback/summary"),
      apiFetch("/feedback/improvement-suggestions"),
      apiFetch("/feedback/recent?helpful=false&limit=10"),
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

function resetCollapsibleResults(details, summary, label, count) {
  details.open = false;
  summary.textContent = `${label}（${count} 道）`;
}

function renderRagEvaluation(data) {
  evaluationMetrics.innerHTML = "";
  resetCollapsibleResults(
    evaluationResultsDetails,
    evaluationResultsSummary,
    "本次检索评测明细",
    data.total_count,
  );
  const retrieval = data.retrieval_metrics;
  const metrics = [
    ["检索策略", getRetrievalStrategyLabel(data.retrieval_strategy)],
    ["通过", `${data.passed_count} / ${data.total_count}`],
    ["Top1 准确率", `${formatRate(retrieval.top1_accuracy)} (${retrieval.top1_correct_count}/${data.total_count})`],
    ["召回率 Recall@3", `${formatRate(retrieval.recall_at_3)} (${retrieval.recalled_count}/${data.total_count})`],
    ["精确率 Precision@3", `${formatRate(retrieval.precision_at_3)} (${retrieval.relevant_result_count}/${retrieval.retrieved_result_count})`],
    ["默认题", data.preset_count],
    ["自定义题", data.custom_count],
  ];
  const metricHints = {
    "Top1 准确率": "目标资料排在第 1 条的题目比例。",
    "召回率 Recall@3": "目标资料进入前 3 条有效检索结果的题目比例。",
    "精确率 Precision@3": "所有有效前 3 条结果中，目标资料所占的比例。",
  };
  for (const [label, value] of metrics) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${label}：${value}`;
    if (metricHints[label]) metric.title = metricHints[label];
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
    const relevance = `有效结果 ${result.retrieved_count} 条，其中目标资料 ${result.relevant_count} 条`;
    if (result.passed) {
      const matchedName = result.matched_name || result.expected_name;
      const isAlternativeMatch = matchedName !== result.expected_name;
      detail.textContent = isAlternativeMatch
        ? `通过：可接受${expectedType}“${matchedName}”命中第 ${result.expected_rank} 条；主目标是“${result.expected_name}”。${relevance}。`
        : `通过：目标${expectedType}“${matchedName}”命中第 ${result.expected_rank} 条。${relevance}。`;
    } else {
      const topResult = result.top_name
        ? `首位结果是${getKnowledgeTypeLabel(result.top_type)}“${result.top_name}”`
        : "没有检索到结果";
      detail.textContent = `未通过：目标${expectedType}“${result.expected_name}”未进入前 3 条；${topResult}。${relevance}。`;
    }
    item.append(title, detail);
    evaluationResults.append(item);
  }
  renderEvaluationQualityGate(data.quality_gate);
}

function formatRate(value) {
  return value === null || value === undefined
    ? "暂无"
    : `${Math.round(value * 100)}%`;
}

function formatPercentagePointDelta(value) {
  const points = Math.round(value * 100);
  return `${points >= 0 ? "+" : ""}${points} 个百分点`;
}

function formatRagasScore(value) {
  return value === null || value === undefined
    ? "无法计算"
    : value.toFixed(3);
}

function getRetrievalStrategyLabel(strategy) {
  return ({
    none: "无检索（直接生成）",
    vector: "仅向量检索",
    hybrid: "混合检索（不重排序）",
    "hybrid-rerank": "混合检索 + 重排序",
  })[strategy] || strategy || "未知策略";
}

function getRagasStatusLabel(status) {
  return ({
    pending: "等待执行",
    running: "正在评测",
    completed: "已完成",
    failed: "执行失败",
  })[status] || "未知状态";
}

function renderRagasEvaluation(run) {
  ragasEvaluationMetrics.innerHTML = "";
  ragasEvaluationResults.innerHTML = "";
  if (!run) {
    ragasEvaluationStatus.className = "ragas-evaluation-status";
    ragasEvaluationStatus.textContent = "尚无 RAGAS 评测记录。默认会随机抽样 10 道已保存的评测题。";
    resetCollapsibleResults(
      ragasEvaluationResultsDetails,
      ragasEvaluationResultsSummary,
      "RAGAS 逐题结果",
      0,
    );
    return;
  }

  const active = ["pending", "running"].includes(run.status);
  ragasEvaluationStatus.className = `ragas-evaluation-status ${run.status}`;
  const createdAt = formatEvaluationTime(run.created_at);
  ragasEvaluationStatus.textContent = active
    ? `任务 #${run.id} ${getRagasStatusLabel(run.status)}：${getRetrievalStrategyLabel(run.retrieval_strategy)}，已完成问答 ${run.completed_count} / ${run.total_count || run.sample_size} 道。`
    : `任务 #${run.id} ${getRagasStatusLabel(run.status)}：${getRetrievalStrategyLabel(run.retrieval_strategy)}，创建于 ${createdAt}。`;
  if (run.error_message) {
    ragasEvaluationStatus.textContent += ` 错误：${run.error_message}`;
  }

  const metrics = run.metrics || {};
  const metricItems = [
    ["检索策略", getRetrievalStrategyLabel(run.retrieval_strategy)],
    ["抽样题数", `${run.total_count || run.sample_size} 道`],
    ["Faithfulness", formatRagasScore(metrics.faithfulness)],
    ["Answer Relevancy", formatRagasScore(metrics.answer_relevancy)],
    ["Context Precision", formatRagasScore(metrics.context_precision)],
    ["Context Recall", formatRagasScore(metrics.context_recall)],
  ];
  for (const [label, value] of metricItems) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${label}：${value}`;
    ragasEvaluationMetrics.append(metric);
  }

  resetCollapsibleResults(
    ragasEvaluationResultsDetails,
    ragasEvaluationResultsSummary,
    "RAGAS 逐题结果",
    run.results.length,
  );
  for (const result of run.results) {
    const item = document.createElement("article");
    item.className = "ragas-evaluation-result";
    const title = document.createElement("h5");
    title.textContent = result.question;
    const detail = document.createElement("p");
    detail.textContent = `目标：${getKnowledgeTypeLabel(result.expected_type)}“${result.expected_name}”｜路径：${result.processing_path}｜有效上下文：${result.retrieved_count} 条`;
    const score = document.createElement("p");
    score.className = "ragas-score-line";
    score.textContent = `Faithfulness ${formatRagasScore(result.faithfulness)}｜Answer Relevancy ${formatRagasScore(result.answer_relevancy)}｜Context Precision ${formatRagasScore(result.context_precision)}｜Context Recall ${formatRagasScore(result.context_recall)}`;
    const context = document.createElement("p");
    context.className = "ragas-context-line";
    context.textContent = result.context_titles.length
      ? `检索资料：${result.context_titles.join("、")}`
      : "检索资料：无";
    const answer = document.createElement("p");
    answer.className = "ragas-answer";
    answer.textContent = `回答：${result.answer}`;
    item.append(title, detail, score, context, answer);
    if (!result.reference_available) {
      const warning = document.createElement("p");
      warning.className = "ragas-warning";
      warning.textContent = "目标参考资料已不存在，Context Precision/Recall 的参考答案已降级为资料名称。";
      item.append(warning);
    }
    if (result.error_message) {
      const error = document.createElement("p");
      error.className = "ragas-warning";
      error.textContent = `评分异常：${result.error_message}`;
      item.append(error);
    }
    ragasEvaluationResults.append(item);
  }
}

async function loadLatestRagasEvaluation() {
  try {
    const response = await apiFetch("/evaluation/ragas/tasks?limit=1");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取 RAGAS 任务失败。"));
    const run = data.runs[0] || null;
    renderRagasEvaluation(run);
    if (run && ["pending", "running"].includes(run.status)) {
      runRagasEvaluationButton.disabled = true;
      runRagasEvaluationButton.textContent = "RAGAS 评测中...";
      watchRagasEvaluation(run.id);
    }
  } catch (error) {
    ragasEvaluationStatus.className = "ragas-evaluation-status error";
    ragasEvaluationStatus.textContent = `读取 RAGAS 任务失败：${error.message}`;
  }
}

async function watchRagasEvaluation(runId) {
  if (ragasEvaluationPollingTimer) {
    window.clearTimeout(ragasEvaluationPollingTimer);
    ragasEvaluationPollingTimer = null;
  }
  try {
    const response = await apiFetch(`/evaluation/ragas/tasks/${runId}`);
    const run = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(run, "读取 RAGAS 任务失败。"));
    renderRagasEvaluation(run);
    if (["pending", "running"].includes(run.status)) {
      ragasEvaluationPollingTimer = window.setTimeout(
        () => watchRagasEvaluation(runId),
        2000,
      );
    } else {
      runRagasEvaluationButton.disabled = false;
      runRagasEvaluationButton.textContent = "运行 RAGAS 评测";
    }
  } catch (error) {
    ragasEvaluationStatus.className = "ragas-evaluation-status error";
    ragasEvaluationStatus.textContent = `读取 RAGAS 任务失败：${error.message}`;
    runRagasEvaluationButton.disabled = false;
    runRagasEvaluationButton.textContent = "运行 RAGAS 评测";
  }
}

async function runRagasEvaluation() {
  const parsedSampleSize = Number.parseInt(ragasSampleSize.value, 10);
  const sampleSize = Number.isFinite(parsedSampleSize)
    ? Math.min(100, Math.max(1, parsedSampleSize))
    : 10;
  ragasSampleSize.value = sampleSize;
  const strategy = evaluationRetrievalStrategy.value;
  const confirmed = window.confirm(
    `将随机抽样 ${sampleSize} 道题，使用“${getRetrievalStrategyLabel(strategy)}”执行 OpenAI 回答生成和 RAGAS 四项评分，会消耗模型额度。确定继续吗？`,
  );
  if (!confirmed) return;

  runRagasEvaluationButton.disabled = true;
  runRagasEvaluationButton.textContent = "正在创建任务...";
  ragasEvaluationStatus.className = "ragas-evaluation-status";
  ragasEvaluationStatus.textContent = "正在创建 RAGAS 评测任务...";
  try {
    const params = new URLSearchParams({
      sample_size: String(sampleSize),
      retrieval_strategy: strategy,
    });
    const response = await apiFetch(`/evaluation/ragas/tasks?${params}`, { method: "POST" });
    const run = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(run, "创建 RAGAS 评测任务失败。"));
    renderRagasEvaluation(run);
    runRagasEvaluationButton.textContent = "RAGAS 评测中...";
    watchRagasEvaluation(run.id);
  } catch (error) {
    ragasEvaluationStatus.className = "ragas-evaluation-status error";
    ragasEvaluationStatus.textContent = `创建 RAGAS 评测任务失败：${error.message}`;
    runRagasEvaluationButton.disabled = false;
    runRagasEvaluationButton.textContent = "运行 RAGAS 评测";
  }
}

function renderMonitoring(data) {
  monitoringMetrics.innerHTML = "";
  const metrics = [
    ["请求数", data.request_count],
    ["检索命中率", data.retrieval_hit_rate === null ? "暂无" : formatRate(data.retrieval_hit_rate)],
    ["答案正确率", formatRate(data.quality.answer_accuracy)],
    ["引用正确率", formatRate(data.quality.citation_accuracy)],
    ["平均耗时", data.average_latency_ms === null ? "暂无" : `${data.average_latency_ms} ms`],
    ["P95 耗时", data.p95_latency_ms === null ? "暂无" : `${data.p95_latency_ms} ms`],
    ["失败率", formatRate(data.failure_rate)],
    ["有帮助率", formatRate(data.feedback.helpful_rate)],
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
    monitoringMetrics.append(metric);
  }

  monitoringPathList.innerHTML = "";
  if (data.path_metrics.length === 0) {
    appendInsight(monitoringPathList, "还没有问答请求记录。先发送一个问题，再刷新监控。 ");
  } else {
    for (const path of data.path_metrics) {
      const item = document.createElement("article");
      item.className = "monitoring-path-item";
      const title = document.createElement("strong");
      title.textContent = path.processing_path;
      const detail = document.createElement("p");
      const hitRate = path.retrieval_hit_rate === null
        ? "不适用"
        : formatRate(path.retrieval_hit_rate);
      detail.textContent = `请求 ${path.request_count} 次｜成功 ${path.success_count}｜失败 ${path.failure_count}｜平均 ${path.average_latency_ms} ms｜命中率 ${hitRate}`;
      item.append(title, detail);
      monitoringPathList.append(item);
    }
  }

  monitoringFailureList.innerHTML = "";
  if (data.recent_failures.length === 0) {
    appendInsight(monitoringFailureList, "当前统计范围内没有失败请求。 ");
  } else {
    for (const failure of data.recent_failures) {
      const item = document.createElement("article");
      item.className = "monitoring-failure-item";
      const title = document.createElement("strong");
      title.textContent = `${failure.status_code}｜${failure.error_type || "未知错误"}`;
      const detail = document.createElement("p");
      detail.textContent = `${failure.endpoint}｜${failure.processing_path}｜耗时 ${failure.latency_ms} ms｜${formatEvaluationTime(failure.created_at)}`;
      item.append(title, detail);
      monitoringFailureList.append(item);
    }
  }
}

async function loadMonitoring() {
  monitoringStatus.textContent = "正在读取运行监控...";
  try {
    const response = await apiFetch(`/monitoring/summary?hours=${monitoringWindow.value}`);
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取监控失败。"));
    renderMonitoring(data);
    monitoringStatus.textContent = `已更新：统计最近 ${data.window_hours} 小时，共 ${data.request_count} 次请求。`;
  } catch (error) {
    monitoringStatus.textContent = `读取失败：${error.message}`;
  }
}

function renderQualityEvaluation(data) {
  const metrics = data.metrics;
  qualityEvaluationMetrics.innerHTML = "";
  resetCollapsibleResults(
    qualityEvaluationResultsDetails,
    qualityEvaluationResultsSummary,
    "答案质量评测明细",
    data.total_count,
  );
  const metricItems = [
    ["检索策略", getRetrievalStrategyLabel(data.retrieval_strategy)],
    ["答案正确率", `${Math.round(metrics.answer_accuracy * 100)}% (${metrics.answer_correct_count}/${metrics.total_count})`],
    ["引用正确率", `${Math.round(metrics.citation_accuracy * 100)}% (${metrics.citation_correct_count}/${metrics.total_count})`],
    ["拒答准确率", `${Math.round(metrics.refusal_accuracy * 100)}% (${metrics.refusal_correct_count}/${metrics.total_count})`],
    ["实际拒答率", `${Math.round(metrics.refusal_rate * 100)}% (${metrics.refusal_observed_count}/${metrics.total_count})`],
  ];
  for (const [label, value] of metricItems) {
    const metric = document.createElement("div");
    metric.className = "evaluation-metric";
    metric.textContent = `${label}：${value}`;
    qualityEvaluationMetrics.append(metric);
  }

  qualityEvaluationResults.innerHTML = "";
  for (const result of data.results) {
    const passed = result.answer_correct && result.citation_correct && result.refusal_correct;
    const item = document.createElement("article");
    item.className = `quality-evaluation-result ${passed ? "passed" : "failed"}`;
    const title = document.createElement("h5");
    title.textContent = result.question;
    const detail = document.createElement("p");
    const answerText = result.expected_refusal
      ? `拒答：${result.refusal_observed ? "已拒答" : "未拒答"}`
      : `答案关键词：${result.answer_match_count}/${result.answer_keyword_count}`;
    const citationText = result.expected_refusal
      ? "拒答题不要求引用"
      : `引用：${result.cited_names.length ? result.cited_names.join("、") : "无"}`;
    detail.textContent = `${answerText}；${citationText}；${result.diagnostic}`;
    item.append(title, detail);
    if (result.missing_answer_keywords.length) {
      const missing = document.createElement("p");
      missing.textContent = `缺少答案关键词：${result.missing_answer_keywords.join("、")}`;
      item.append(missing);
    }
    if (result.missing_citation_names.length) {
      const missing = document.createElement("p");
      missing.textContent = `缺少引用资料：${result.missing_citation_names.join("、")}`;
      item.append(missing);
    }
    qualityEvaluationResults.append(item);
  }
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
  resetCollapsibleResults(
    comparisonResultsDetails,
    comparisonResultsSummary,
    "新旧检索对比明细",
    data.total_count,
  );
  const metrics = [
    ["基线策略", getRetrievalStrategyLabel(data.baseline_strategy)],
    ["当前策略", getRetrievalStrategyLabel(data.current_strategy)],
    ["旧策略", `${data.baseline.passed_count} / ${data.total_count} (${Math.round(data.baseline.pass_rate * 100)}%)`],
    ["新策略", `${data.current.passed_count} / ${data.total_count} (${Math.round(data.current.pass_rate * 100)}%)`],
    ["Top1 准确率（旧 -> 新）", `${formatRate(data.baseline.metrics.top1_accuracy)} -> ${formatRate(data.current.metrics.top1_accuracy)}（${formatPercentagePointDelta(data.top1_accuracy_delta)}）`],
    ["召回率 Recall@3（旧 -> 新）", `${formatRate(data.baseline.metrics.recall_at_3)} -> ${formatRate(data.current.metrics.recall_at_3)}（${formatPercentagePointDelta(data.recall_at_3_delta)}）`],
    ["精确率 Precision@3（旧 -> 新）", `${formatRate(data.baseline.metrics.precision_at_3)} -> ${formatRate(data.current.metrics.precision_at_3)}（${formatPercentagePointDelta(data.precision_at_3_delta)}）`],
    ["命中率变化", formatPercentagePointDelta(data.pass_rate_delta)],
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
  resetCollapsibleResults(
    diagnosisResultsDetails,
    diagnosisResultsSummary,
    "检索诊断明细",
    data.total_count,
  );
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
  resetCollapsibleResults(
    customEvaluationDetails,
    customEvaluationSummary,
    "已保存的自定义评测题",
    data.total_count,
  );
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
    const qualityHints = item.expected_refusal
      ? "｜质量评测：应拒答"
      : `｜答案关键词：${item.answer_keywords.length || "默认资料名称"}｜引用：${item.citation_names.length || "默认资料名称"}`;
    text.textContent = `问题：${item.question}｜分类：${item.category}｜目标${getKnowledgeTypeLabel(item.expected_type)}：${item.expected_name}${alternatives}${qualityHints}`;
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
    detail.textContent = `策略：${getRetrievalStrategyLabel(run.retrieval_strategy)}；默认题 ${run.preset_count} 道，自定义题 ${run.custom_count} 道，知识库资料 ${run.knowledge_document_count} 条`;
    item.append(summary, detail);
    evaluationHistoryList.append(item);
  }
}

async function loadEvaluationHistory() {
  evaluationHistoryStatus.textContent = "正在读取评测历史...";
  try {
    const response = await apiFetch("/evaluation/history?limit=10");
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
    const response = await apiFetch("/evaluation/cases");
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
    answer_keywords: [...new Set(
      customEvaluationAnswerKeywords.value
        .split(/[，,、]/)
        .map((keyword) => keyword.trim())
        .filter(Boolean),
    )],
    citation_names: [...new Set(
      customEvaluationCitationNames.value
        .split(/[，,、]/)
        .map((name) => name.trim())
        .filter(Boolean),
    )],
    expected_refusal: customEvaluationExpectedRefusal.checked,
    expected_type: customEvaluationExpectedType.value,
  };
  customEvaluationStatus.textContent = "正在保存自定义题...";
  try {
    const response = await apiFetch("/evaluation/cases", {
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
    const response = await apiFetch(`/evaluation/cases/${caseId}`, { method: "DELETE" });
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
    const strategy = evaluationRetrievalStrategy.value;
    const response = await apiFetch(
      `/evaluation/run?retrieval_strategy=${encodeURIComponent(strategy)}`,
      { method: "POST" },
    );
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

async function runQualityEvaluation() {
  const confirmed = window.confirm(
    "将检查答案关键词、引用资料位置和拒答行为，只调用 Embedding，不生成模型回答。确定继续吗？",
  );
  if (!confirmed) return;

  runQualityEvaluationButton.disabled = true;
  runQualityEvaluationButton.textContent = "正在评估...";
  qualityEvaluationStatus.className = "quality-evaluation-status";
  qualityEvaluationStatus.textContent = "正在核对答案证据、引用和拒答题...";
  qualityEvaluationMetrics.innerHTML = "";
  qualityEvaluationResults.innerHTML = "";
  try {
    const response = await apiFetch(
      `/evaluation/quality?retrieval_strategy=${encodeURIComponent(evaluationRetrievalStrategy.value)}`,
      { method: "POST" },
    );
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "回答质量评估失败。"));
    renderQualityEvaluation(data);
    const { metrics } = data;
    qualityEvaluationStatus.textContent = `评估完成：共 ${metrics.total_count} 道题，其中 ${metrics.refusal_expected_count} 道是拒答题。`;
  } catch (error) {
    qualityEvaluationStatus.className = "quality-evaluation-status error";
    qualityEvaluationStatus.textContent = `评估失败：${error.message}`;
  } finally {
    runQualityEvaluationButton.disabled = false;
    runQualityEvaluationButton.textContent = "评估回答质量";
  }
}

async function compareRetrievalStrategies() {
  const confirmed = window.confirm(
    `将对比“${getRetrievalStrategyLabel(comparisonBaselineStrategy.value)}”和“${getRetrievalStrategyLabel(evaluationRetrievalStrategy.value)}”，只调用 Embedding，不生成模型回答，可能消耗少量额度。确定继续吗？`,
  );
  if (!confirmed) return;

  compareRetrievalButton.disabled = true;
  compareRetrievalButton.textContent = "正在对比...";
  comparisonStatus.className = "comparison-status";
  comparisonStatus.textContent = "正在执行所选的两套检索策略...";
  comparisonMetrics.innerHTML = "";
  comparisonResults.innerHTML = "";
  try {
    const params = new URLSearchParams({
      baseline_strategy: comparisonBaselineStrategy.value,
      current_strategy: evaluationRetrievalStrategy.value,
    });
    const response = await apiFetch(`/evaluation/compare?${params}`, { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "检索对比失败。"));
    renderRetrievalComparison(data);
    comparisonStatus.textContent = "对比完成。结果中的策略名称就是本次实际执行的配置。";
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
    const response = await apiFetch(
      `/evaluation/diagnose?retrieval_strategy=${encodeURIComponent(evaluationRetrievalStrategy.value)}`,
      { method: "POST" },
    );
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

function getReviewTargetKey(item) {
  return `${item.type}:${item.record_id}`;
}

function syncReviewBatchControls() {
  const selectedCount = selectedReviewTargets.size;
  reviewBatchSubmitButton.disabled = selectedCount === 0;
  reviewBatchSubmitButton.textContent = selectedCount === 0
    ? "选择资料后批量审核"
    : `批量审核已选 ${selectedCount} 条资料`;
}

function renderReviewQueue(data) {
  reviewResults.innerHTML = "";
  const availableKeys = new Set(data.results.map(getReviewTargetKey));
  for (const key of selectedReviewTargets.keys()) {
    if (!availableKeys.has(key)) selectedReviewTargets.delete(key);
  }
  if (data.results.length === 0) {
    reviewStatus.textContent = "目前没有待核验资料。";
    syncReviewBatchControls();
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
    const selectLabel = document.createElement("label");
    selectLabel.className = "review-select";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = selectedReviewTargets.has(getReviewTargetKey(item));
    checkbox.addEventListener("change", () => {
      const key = getReviewTargetKey(item);
      if (checkbox.checked) {
        selectedReviewTargets.set(key, { type: item.type, record_id: item.record_id });
      } else {
        selectedReviewTargets.delete(key);
      }
      syncReviewBatchControls();
    });
    const selectText = document.createElement("span");
    selectText.textContent = "选择";
    selectLabel.append(checkbox, selectText);
    header.append(title, type, selectLabel);

    const metadata = document.createElement("p");
    metadata.textContent = `来源：${item.source || "未标注来源"} | 可信度：${getSourceTierLabel(item.source_tier)} | 更新：${formatUpdatedAt(item.updated_at)}`;
    const sourceUrlLink = createSourceUrlLink(item.source_url);
    const reasons = document.createElement("p");
    reasons.className = "review-reasons";
    reasons.textContent = `需处理：${item.review_reasons.join("；")}`;
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.textContent = "去补充来源";
    editButton.addEventListener("click", () => openEditDialog(item));
    result.append(header, metadata);
    if (sourceUrlLink) result.append(sourceUrlLink);
    result.append(reasons, editButton);
    reviewResults.append(result);
  }
  syncReviewBatchControls();
}

async function loadReviewQueue() {
  reviewStatus.className = "review-status";
  reviewStatus.textContent = "正在读取待核验资料...";
  reviewResults.innerHTML = "";
  refreshReviewQueueButton.disabled = true;
  try {
    const response = await apiFetch("/knowledge/review-queue");
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

async function submitReviewBatch(event) {
  event.preventDefault();
  if (selectedReviewTargets.size === 0) return;

  const payload = {
    ...Object.fromEntries(new FormData(reviewBatchForm).entries()),
    targets: [...selectedReviewTargets.values()],
  };
  reviewBatchSubmitButton.disabled = true;
  reviewBatchStatus.className = "review-batch-status";
  reviewBatchStatus.textContent = "正在保存审核信息...";
  try {
    const response = await apiFetch("/knowledge/review-queue/batch-update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "批量审核失败。"));
    selectedReviewTargets.clear();
    reviewBatchForm.reset();
    reviewBatchForm.elements.source_tier.value = "professional";
    reviewBatchStatus.textContent = `已保存 ${data.updated_count} 条资料的审核信息。知识库已变为待重建状态。`;
    await Promise.all([
      loadKnowledgeStatus(),
      loadReviewQueue(),
      loadReviewHistory(),
      loadKnowledgeVersions(),
    ]);
    if (searchInput.value.trim()) searchForm.requestSubmit();
  } catch (error) {
    reviewBatchStatus.className = "review-batch-status error";
    reviewBatchStatus.textContent = `批量审核失败：${error.message}`;
  } finally {
    syncReviewBatchControls();
  }
}

function renderReviewHistory(data) {
  reviewHistoryResults.innerHTML = "";
  if (data.logs.length === 0) {
    reviewHistoryStatus.textContent = "还没有审核记录。完成一次批量审核后会自动保存。";
    return;
  }

  reviewHistoryStatus.textContent = `共保存 ${data.total_count} 条审核记录，当前显示最近 ${data.logs.length} 条。`;
  for (const log of data.logs) {
    const item = document.createElement("article");
    item.className = "review-history-item";
    const header = document.createElement("div");
    header.className = "search-result-header";
    const title = document.createElement("h4");
    title.textContent = log.record_title;
    const type = document.createElement("span");
    type.className = `type-chip ${log.record_type}`;
    type.textContent = getKnowledgeTypeLabel(log.record_type);
    header.append(title, type);
    const detail = document.createElement("p");
    detail.textContent = `审核时间：${formatUpdatedAt(log.created_at)} | 来源：${log.source} | 可信度：${getSourceTierLabel(log.source_tier)}`;
    item.append(header, detail);
    const sourceUrlLink = createSourceUrlLink(log.source_url);
    if (sourceUrlLink) item.append(sourceUrlLink);
    reviewHistoryResults.append(item);
  }
}

async function loadReviewHistory() {
  reviewHistoryStatus.className = "review-history-status";
  reviewHistoryStatus.textContent = "正在读取审核记录...";
  reviewHistoryResults.innerHTML = "";
  refreshReviewHistoryButton.disabled = true;
  try {
    const response = await apiFetch("/knowledge/review-logs");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取审核记录失败。"));
    renderReviewHistory(data);
  } catch (error) {
    reviewHistoryStatus.className = "review-history-status error";
    reviewHistoryStatus.textContent = `读取失败：${error.message}`;
  } finally {
    refreshReviewHistoryButton.disabled = false;
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
    const response = await apiFetch("/knowledge/versions");
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

function renderRebuildJobHistory(data) {
  rebuildHistoryResults.innerHTML = "";
  if (data.jobs.length === 0) {
    rebuildHistoryStatus.textContent = "还没有重建任务记录。点击一次“重建知识库”后会自动保存。";
    return;
  }

  rebuildHistoryStatus.textContent = `共 ${data.total_count} 次重建，当前显示最近 ${data.jobs.length} 次。`;
  for (const job of data.jobs) {
    const item = document.createElement("article");
    item.className = "rebuild-job-item";
    const header = document.createElement("div");
    header.className = "search-result-header";
    const title = document.createElement("h4");
    title.textContent = `任务 #${job.id}`;
    const state = document.createElement("span");
    state.className = `job-status ${job.status}`;
    state.textContent = getRebuildStatusLabel(job.status);
    header.append(title, state);

    const detail = document.createElement("p");
    const createdAt = formatUpdatedAt(job.created_at);
    const completedAt = job.completed_at ? ` | 结束：${formatUpdatedAt(job.completed_at)}` : "";
    detail.textContent = `创建：${createdAt} | ${job.document_count} 份资料 | ${job.chunk_count} 个切块${completedAt}`;
    item.append(header, detail);

    if (job.error_message) {
      const error = document.createElement("p");
      error.className = "rebuild-job-error";
      error.textContent = `失败原因：${job.error_message}`;
      item.append(error);
    }
    if (job.retry_of_job_id) {
      const retrySource = document.createElement("p");
      retrySource.textContent = `本任务重试自任务 #${job.retry_of_job_id}`;
      item.append(retrySource);
    }
    if (job.status === "failed") {
      const retryButton = document.createElement("button");
      retryButton.type = "button";
      retryButton.textContent = "重新执行";
      retryButton.addEventListener("click", () => retryRebuildJob(job, retryButton));
      item.append(retryButton);
    }
    rebuildHistoryResults.append(item);
  }
}

async function loadRebuildJobHistory() {
  rebuildHistoryStatus.className = "rebuild-history-status";
  rebuildHistoryStatus.textContent = "正在读取重建任务...";
  rebuildHistoryResults.innerHTML = "";
  refreshRebuildHistoryButton.disabled = true;
  try {
    const response = await apiFetch("/knowledge/rebuild/jobs?limit=20");
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取重建任务失败。"));
    renderRebuildJobHistory(data);
  } catch (error) {
    rebuildHistoryStatus.className = "rebuild-history-status error";
    rebuildHistoryStatus.textContent = `读取失败：${error.message}`;
  } finally {
    refreshRebuildHistoryButton.disabled = false;
  }
}

async function retryRebuildJob(job, button) {
  const confirmed = window.confirm(
    `任务 #${job.id} 失败，确定重新生成全部资料的向量吗？这可能消耗 OpenAI Embedding 额度。`,
  );
  if (!confirmed) return;

  button.disabled = true;
  button.textContent = "正在创建重试任务...";
  try {
    const response = await apiFetch(`/knowledge/rebuild/jobs/${job.id}/retry`, {
      method: "POST",
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "创建重试任务失败。"));
    await Promise.all([watchRebuildJob(data.id), loadRebuildJobHistory()]);
  } catch (error) {
    rebuildHistoryStatus.className = "rebuild-history-status error";
    rebuildHistoryStatus.textContent = `重试失败：${error.message}`;
    button.disabled = false;
    button.textContent = "重新执行";
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
    const response = await apiFetch(`/knowledge/versions/${version.id}/restore`, {
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
    const sourceUrlLink = createSourceUrlLink(item.source_url);
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
    result.append(header, fields, excerpt);
    if (sourceUrlLink) result.append(sourceUrlLink);
    result.append(actions);
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
    const response = await apiFetch(`/knowledge/search?q=${encodeURIComponent(query)}`);
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
    const response = await apiFetch(endpoint, {
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
  const files = Array.from(uploadFile.files);
  if (files.length === 0) return;

  const submitButton = uploadForm.querySelector("button[type='submit']");
  const formData = new FormData();
  for (const file of files) formData.append("files", file);
  entryStatus.className = "manager-status";
  entryStatus.textContent = `正在上传 ${files.length} 个文件...`;
  submitButton.disabled = true;

  try {
    const response = await apiFetch("/documents/upload-batch", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "上传失败。"));
    uploadForm.reset();
    const failedNames = data.errors.map((item) => `${item.filename}（${item.detail}）`);
    entryStatus.textContent = `成功导入 ${data.created_count} 个文件，新增 ${data.created_document_count} 条资料，失败 ${data.failed_count} 个。知识库已变为待重建状态。${failedNames.length ? ` 失败：${failedNames.join("、")}` : ""}`;
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

async function importWebKnowledge(event) {
  event.preventDefault();
  const submitButton = webImportForm.querySelector("button[type='submit']");
  const payload = Object.fromEntries(new FormData(webImportForm).entries());
  entryStatus.className = "manager-status";
  entryStatus.textContent = "正在读取网页资料...";
  submitButton.disabled = true;

  try {
    const response = await apiFetch("/documents/import-web", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "网页导入失败。"));
    webImportForm.reset();
    entryStatus.textContent = `已导入网页资料“${data.title}”。知识库已变为待重建状态。`;
    await loadKnowledgeStatus();
    await loadReviewQueue();
    await loadKnowledgeVersions();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `网页导入失败：${error.message}`;
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
    const response = await apiFetch(`${config.endpoint}/${item.record_id}`);
    const data = await response.json();
    if (!response.ok) throw new Error(getErrorMessage(data, "读取资料失败。"));
    activeEdit = { id: item.record_id, type: item.type, config };
    editTitle.textContent = `编辑${config.label}：${data.name || data.title}`;
    editFields.innerHTML = "";
    for (const [name, label, controlType, inputType] of config.fields) {
      const fieldLabel = document.createElement("label");
      fieldLabel.textContent = label;
      const control = document.createElement(controlType);
      control.name = name;
      control.required = name !== "source_url";
      if (inputType) control.type = inputType;
      if (controlType === "select") {
        for (const [value, optionLabel] of SOURCE_TIER_OPTIONS) {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = optionLabel;
          control.append(option);
        }
      }
      control.value = data[name] || "";
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
    const response = await apiFetch(
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
    const response = await apiFetch(`${config.endpoint}/${item.record_id}`, {
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
  const response = await apiFetch("/ask/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      conversation_id: conversationId,
      knowledge_type: retrievalScopeSelect.value,
      source_filter: sourceFilterSelect.value,
    }),
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
  if (!requireLoginForKnowledge()) return;
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage(question, "user");
  questionInput.value = "";
  sendButton.disabled = true;
  sendButton.textContent = "正在查询";

  try {
    await requestStreamingAnswer(question);
    loadConversationList();
    loadMemoryOverview();
  } catch (error) {
    appendMessage(`暂时无法回答：${error.message}`, "assistant");
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "发送";
    questionInput.focus();
  }
});

newChatButton.addEventListener("click", resetConversation);
exportConversationButton.addEventListener("click", exportConversation);
accountToggleButton.addEventListener("click", openAccountDialog);
accountDialogCloseButton.addEventListener("click", closeAccountDialog);
accountForm.addEventListener("submit", submitAccount);
accountLogoutButton.addEventListener("click", logoutAccount);
refreshMemoryButton.addEventListener("click", loadMemoryOverview);
document.querySelectorAll("[data-account-mode]").forEach((tab) => {
  tab.addEventListener("click", () => setAccountMode(tab.dataset.accountMode));
});
refreshHistoryButton.addEventListener("click", loadConversationList);
rebuildKnowledgeButton.addEventListener("click", () => {
  if (requireAdminForManagement()) rebuildKnowledge();
});
refreshReviewQueueButton.addEventListener("click", loadReviewQueue);
reviewBatchForm.addEventListener("submit", submitReviewBatch);
refreshReviewHistoryButton.addEventListener("click", loadReviewHistory);
refreshKnowledgeVersionsButton.addEventListener("click", loadKnowledgeVersions);
refreshRebuildHistoryButton.addEventListener("click", loadRebuildJobHistory);
runRagEvaluationButton.addEventListener("click", runRagEvaluation);
runQualityEvaluationButton.addEventListener("click", runQualityEvaluation);
runRagasEvaluationButton.addEventListener("click", runRagasEvaluation);
compareRetrievalButton.addEventListener("click", compareRetrievalStrategies);
diagnoseRetrievalButton.addEventListener("click", diagnoseCurrentRetrieval);
refreshEvaluationHistoryButton.addEventListener("click", loadEvaluationHistory);
customEvaluationForm.addEventListener("submit", addCustomEvaluationCase);
managerToggleButton.addEventListener("click", () => {
  if (!requireAdminForManagement()) return;
  setManagerVisible(knowledgeManager.classList.contains("is-hidden"));
});
feedbackDashboardToggle.addEventListener("click", () => {
  if (!requireAdminForManagement()) return;
  setFeedbackDashboardVisible(qualityDashboard.classList.contains("is-hidden"));
});
refreshFeedbackButton.addEventListener("click", loadFeedbackDashboard);
refreshMonitoringButton.addEventListener("click", loadMonitoring);
monitoringWindow.addEventListener("change", loadMonitoring);
searchForm.addEventListener("submit", searchKnowledge);
uploadForm.addEventListener("submit", uploadKnowledgeFile);
webImportForm.addEventListener("submit", importWebKnowledge);
editForm.addEventListener("submit", saveEdit);
document.querySelector("#edit-cancel").addEventListener("click", closeEditDialog);
document.querySelector("#edit-cancel-bottom").addEventListener("click", closeEditDialog);
document.querySelector("#reference-dialog-close").addEventListener("click", closeReferenceDialog);
document.querySelector("#reference-dialog-close-bottom").addEventListener("click", closeReferenceDialog);
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
setAccountMode("login");
updatePermissionUI();
loadCurrentUser();
saveActiveConversation();

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
