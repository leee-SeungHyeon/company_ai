// ===== 페이지 네비게이션 =====
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        item.classList.add('active');
        document.getElementById(`page-${item.dataset.page}`).classList.add('active');
    });
});

// ===== 사규 Q&A =====
const qaInput = document.getElementById('qa-input');
const qaSubmit = document.getElementById('qa-submit');
const chatMessages = document.getElementById('chat-messages');

function clearEmpty() {
    const empty = chatMessages.querySelector('.chat-empty');
    if (empty) empty.remove();
}

function addMessage(text, role) {
    clearEmpty();
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

qaSubmit.addEventListener('click', async () => {
    const query = qaInput.value.trim();
    if (!query || qaSubmit.disabled) return;

    addMessage(query, 'user');
    qaInput.value = '';
    qaInput.style.height = 'auto';
    qaSubmit.disabled = true;

    const loading = addMessage('답변을 생성하는 중...', 'ai loading');

    try {
        const res = await fetch('/api/qa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        loading.textContent = data.answer;
        loading.classList.remove('loading');
    } catch {
        loading.textContent = '오류가 발생했습니다. 다시 시도해주세요.';
        loading.classList.remove('loading');
    } finally {
        qaSubmit.disabled = false;
        qaInput.focus();
    }
});

// Enter 전송 (Shift+Enter 줄바꿈)
qaInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        qaSubmit.click();
    }
});

// textarea 자동 높이 조절
qaInput.addEventListener('input', () => {
    qaInput.style.height = 'auto';
    qaInput.style.height = Math.min(qaInput.scrollHeight, 120) + 'px';
});

// ===== 이메일 작성 =====
const emailInput = document.getElementById('email-input');
const emailSubmit = document.getElementById('email-submit');
const emailPlaceholder = document.getElementById('email-placeholder');
const emailResult = document.getElementById('email-result');
const emailSubject = document.getElementById('email-subject');
const emailBody = document.getElementById('email-body');
const emailCopy = document.getElementById('email-copy');

emailSubmit.addEventListener('click', async () => {
    const request = emailInput.value.trim();
    if (!request || emailSubmit.disabled) return;

    emailSubmit.disabled = true;
    emailSubmit.textContent = '생성 중...';
    emailPlaceholder.style.display = 'flex';
    emailResult.style.display = 'none';

    try {
        const res = await fetch('/api/email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ request }),
        });
        if (!res.ok) throw new Error();
        const data = await res.json();

        emailSubject.textContent = data.subject;
        emailBody.textContent = data.body;
        emailPlaceholder.style.display = 'none';
        emailResult.style.display = 'flex';
    } catch {
        alert('오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
        emailSubmit.disabled = false;
        emailSubmit.textContent = '이메일 생성';
    }
});

emailCopy.addEventListener('click', () => {
    const text = `제목: ${emailSubject.textContent}\n\n${emailBody.textContent}`;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => showCopied());
    } else {
        // fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showCopied();
    }
});

function showCopied() {
    emailCopy.textContent = '✅ 복사됨';
    setTimeout(() => { emailCopy.textContent = '📋 복사'; }, 2000);
}
