const form = document.getElementById("chat-form");
const input = document.getElementById("query-input");
const messages = document.getElementById("messages");

function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
}

function createMessage(role, text) {
    const article = document.createElement("article");
    article.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const paragraph = document.createElement("p");
    paragraph.textContent = text;

    bubble.appendChild(paragraph);
    article.appendChild(avatar);
    article.appendChild(bubble);
    messages.appendChild(article);
    scrollToBottom();

    return paragraph;
}

function autoResize() {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
}

input.addEventListener("input", autoResize);

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = input.value.trim();
    if (!query) {
        return;
    }

    const sendButton = form.querySelector("button");
    sendButton.disabled = true;

    createMessage("user", query);
    input.value = "";
    autoResize();

    try {
        const response = await fetch("/api/query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();

        if (!response.ok) {
            createMessage("assistant", data.error || "Something went wrong.");
            return;
        }

        if (data.reply && data.reply.trim()) {
            createMessage("assistant", data.reply);
        } else {
            createMessage(
                "assistant",
                "Query received. Implement the response logic in process_query() later.",
            );
        }
    } catch (error) {
        createMessage(
            "assistant",
            "Unable to reach the backend. Check that Flask is running.",
        );
    } finally {
        sendButton.disabled = false;
        input.focus();
    }
});

autoResize();
