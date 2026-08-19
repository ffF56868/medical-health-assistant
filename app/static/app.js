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

let conversationId = createConversationId();

function createConversationId() {
  return `web-${crypto.randomUUID()}`;
}

function scrollToLatestMessage() {
  messageList.scrollTop = messageList.scrollHeight;
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
  text.textContent = content;
  message.append(text);

  if (references.length > 0) {
    const referenceSection = document.createElement("section");
    referenceSection.className = "references";
    const title = document.createElement("h3");
    title.textContent = "参考资料";
    referenceSection.append(title);

    for (const reference of references) {
      const item = referenceTemplate.content.cloneNode(true);
      item.querySelector(".reference-name").textContent = reference.name;
      item.querySelector(".reference-score").textContent = `相关度 ${Math.round(reference.relevance_score * 100)}%`;
      item.querySelector(".reference-source").textContent = reference.source || reference.type;
      item.querySelector(".reference-excerpt").textContent = reference.excerpt;
      referenceSection.append(item);
    }
    message.append(referenceSection);
  }

  if (role === "assistant" && assistantMessageId) {
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

  messageList.append(message);
  scrollToLatestMessage();
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
  messageList.innerHTML = "";
  appendMessage("已开始新的对话。你可以继续向我询问健康资料中的内容。", "assistant");
  questionInput.focus();
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
  messageList.classList.toggle("is-hidden", visible);
  form.classList.toggle("is-hidden", visible);
  managerToggleButton.textContent = visible ? "返回问答" : "管理资料";
  if (visible) searchInput.focus();
}

function getErrorMessage(data, fallback) {
  return data?.detail || fallback;
}

function clearSearchResults() {
  searchResults.innerHTML = "";
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
    type.textContent = ({ condition: "病症", drug: "药物", document: "资料" })[item.type] || item.type;
    header.append(title, type);
    const fields = document.createElement("p");
    fields.textContent = `匹配字段：${item.matched_fields.join("、")}${item.source ? ` | 来源：${item.source}` : ""}`;
    const excerpt = document.createElement("p");
    excerpt.textContent = item.excerpt;
    result.append(header, fields, excerpt);
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
    if (endpoint === "/documents") formElement.elements.source.value = "manual";
    entryStatus.textContent = `已保存“${data.name || data.title}”。知识库已变为待重建状态。`;
    await loadKnowledgeStatus();
  } catch (error) {
    entryStatus.className = "manager-status error";
    entryStatus.textContent = `保存失败：${error.message}`;
  } finally {
    submitButton.disabled = false;
  }
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
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, conversation_id: conversationId }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "请求失败，请稍后再试。");
    appendMessage(
      data.answer,
      "assistant",
      data.references || [],
      data.assistant_message_id,
    );
  } catch (error) {
    appendMessage(`暂时无法回答：${error.message}`, "assistant");
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "发送";
    questionInput.focus();
  }
});

newChatButton.addEventListener("click", resetConversation);
rebuildKnowledgeButton.addEventListener("click", rebuildKnowledge);
managerToggleButton.addEventListener("click", () => {
  setManagerVisible(knowledgeManager.classList.contains("is-hidden"));
});
searchForm.addEventListener("submit", searchKnowledge);
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

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
