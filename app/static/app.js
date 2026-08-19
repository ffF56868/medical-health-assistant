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

const entryConfiguration = {
  condition: {
    endpoint: "/conditions",
    label: "病症",
    fields: [
      ["name", "病症名称", "input"],
      ["symptoms", "常见症状", "textarea"],
      ["treatment", "通用处理建议", "textarea"],
    ],
  },
  drug: {
    endpoint: "/drugs",
    label: "药物",
    fields: [
      ["name", "药物名称", "input"],
      ["effects", "药物作用", "textarea"],
      ["instructions", "使用说明", "textarea"],
    ],
  },
  document: {
    endpoint: "/documents",
    label: "资料",
    fields: [
      ["title", "资料标题", "input"],
      ["source", "资料来源", "input"],
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
    item.querySelector(".reference-source").textContent = reference.source || reference.type;
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
      control.value = data[name];
      if (controlType === "textarea") control.rows = name === "content" ? 8 : 4;
      fieldLabel.append(control);
      editFields.append(fieldLabel);
    }
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
managerToggleButton.addEventListener("click", () => {
  setManagerVisible(knowledgeManager.classList.contains("is-hidden"));
});
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
