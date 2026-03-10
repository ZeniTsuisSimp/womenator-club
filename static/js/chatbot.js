/* ===========================================
   Womenovators Club - Chatbot JavaScript
   =========================================== */

document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.querySelector('.chatbot-toggle');
    const chatWindow = document.querySelector('.chatbot-window');
    const closeBtn = document.querySelector('.chatbot-close');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messages = document.querySelector('.chatbot-messages');

    if (!toggle || !chatWindow) return;

    // Toggle chat window
    toggle.addEventListener('click', () => {
        chatWindow.classList.toggle('open');
        if (chatWindow.classList.contains('open') && messages.children.length === 0) {
            addMessage('bot', "Hi! 👋 I'm the Womenovators assistant. Ask me about events, membership, workshops, or anything about our club!");
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => chatWindow.classList.remove('open'));
    }

    // Session ID
    const sessionId = 'chat_' + Math.random().toString(36).substr(2, 9);

    // Send message
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const msg = input.value.trim();
            if (!msg) return;

            addMessage('user', msg);
            input.value = '';

            // Typing indicator
            const typing = document.createElement('div');
            typing.className = 'chat-msg bot typing';
            typing.innerHTML = '<em>Typing...</em>';
            messages.appendChild(typing);
            messages.scrollTop = messages.scrollHeight;

            fetch('/api/chatbot/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `message=${encodeURIComponent(msg)}&session_id=${sessionId}`
            })
            .then(r => r.json())
            .then(data => {
                typing.remove();
                addMessage('bot', data.response || "Sorry, I couldn't understand that.");
            })
            .catch(() => {
                typing.remove();
                addMessage('bot', "Sorry, something went wrong. Please try again.");
            });
        });
    }

    function addMessage(type, text) {
        const div = document.createElement('div');
        div.className = `chat-msg ${type}`;
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }
});
