const form = document.querySelector("#ask-form");
const questionInput = document.querySelector("#question");
const messageList = document.querySelector("#message-list");
const sendButton = document.querySelector("#send-button");
const newChatButton = document.querySelector("#new-chat");
const referenceTemplate = document.querySelector("#reference-template");

let conversationId = createConversationId();

function createConversationId() {
  return `web-${crypto.randomUUID()}`;
}

function scrollToLatestMessage() {
  messageList.scrollTop = messageList.scrollHeight;
}

function appendMessage(content, role, references = []) {
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

  messageList.append(message);
  scrollToLatestMessage();
}

function resetConversation() {
  conversationId = createConversationId();
  messageList.innerHTML = "";
  appendMessage("已开始新的对话。你可以继续向我询问健康资料中的内容。", "assistant");
  questionInput.focus();
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
    appendMessage(data.answer, "assistant", data.references || []);
  } catch (error) {
    appendMessage(`暂时无法回答：${error.message}`, "assistant");
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "发送";
    questionInput.focus();
  }
});

newChatButton.addEventListener("click", resetConversation);

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
