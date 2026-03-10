/* ===========================================
   Womenovators Club - Wiva Chatbot
   =========================================== */

document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.querySelector('.chatbot-toggle');
    const chatWindow = document.querySelector('.chatbot-window');
    const closeBtn = document.querySelector('.chatbot-close');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messages = document.querySelector('.chatbot-messages');
    const quickBtns = document.querySelectorAll('.quick-action-btn');

    if (!toggle || !chatWindow) return;

    // Toggle chat window
    toggle.addEventListener('click', () => {
        chatWindow.classList.toggle('open');
        if (chatWindow.classList.contains('open') && messages.children.length === 0) {
            addMessage('bot', "Hey there! 💜 I'm <strong>Wiva</strong>, your Womenovators AI assistant. Ask me anything about the club!");
        }
        if (chatWindow.classList.contains('open')) input.focus();
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => chatWindow.classList.remove('open'));
    }

    // Session ID
    const sessionId = 'chat_' + Math.random().toString(36).substr(2, 9);

    // Quick action buttons
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const msg = btn.getAttribute('data-msg');
            if (msg) sendMessage(msg);
        });
    });

    // Send message on form submit
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const msg = input.value.trim();
            if (!msg) return;
            sendMessage(msg);
        });
    }

    function sendMessage(msg) {
        addMessage('user', msg);
        input.value = '';

        // Typing indicator
        const typing = document.createElement('div');
        typing.className = 'chat-msg bot typing';
        typing.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span> Wiva is thinking...';
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
            addMessage('bot', "Oops! Something went wrong. Please try again. 🔄");
        });
    }

    function addMessage(type, text) {
        const div = document.createElement('div');
        div.className = `chat-msg ${type}`;
        if (type === 'bot') {
            div.innerHTML = text;
        } else {
            div.textContent = text;
        }
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }
});
