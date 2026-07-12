/* ==========================================================================
   FandomDial — WhatsApp Web style frontend
   Plain HTML/CSS/JS, no frameworks, no build tools.
   ========================================================================== */

(function () {
  "use strict";

  /* ---------- Session ---------- */
  const sessionId = generateId();

  function generateId() {
    if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
    return "sess-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
  }

  /* ---------- State ---------- */
  let characters = [];
  let activeCharacter = null;
  let language = "en"; // "en" | "hi"
  let sending = false;

  // audio cache: key `${characterId}::${text}` -> blob URL
  const audioCache = new Map();
  // race-condition ticket
  let voiceTicket = 0;
  let currentAudio = null;
  // tracks which bubble button currently owns the "active" ticket, for state resets
  let currentPlayingBtn = null;

  const FILLER_INDICES = {
    gullu: [1, 2],
    sohail: [2],
    zaid: [1, 2],
  };

  const CHARACTER_AVATARS = {
    gullu: "🙂",
    sohail: "🧔",
    zaid: "😎",
  };

  /* ---------- Profile (remembered locally) ---------- */
  const PROFILE_KEY = "fandomdial_profile";
  const DEFAULT_AVATAR =
    "data:image/svg+xml;utf8," +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="80" height="80" fill="%23128c7e"/><text x="50%" y="55%" font-size="34" fill="%23fff" text-anchor="middle" font-family="sans-serif">?</text></svg>',
    );

  function loadProfile() {
    try {
      const raw = localStorage.getItem(PROFILE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {
      /* ignore corrupt storage */
    }
    return { name: "You", avatar: DEFAULT_AVATAR };
  }

  function saveProfile(profile) {
    try {
      localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
    } catch (e) {
      /* storage unavailable — feature degrades silently */
    }
  }

  let profile = loadProfile();

  function renderProfile() {
    document.getElementById("my-name").textContent = profile.name || "You";
    document.getElementById("my-avatar").src = profile.avatar || DEFAULT_AVATAR;
    document.getElementById("my-avatar").alt = profile.name || "You";
  }

  /* ---------- DOM refs ---------- */
  const contactListEl = document.getElementById("contact-list");
  const emptyStateEl = document.getElementById("empty-state");
  const chatActiveEl = document.getElementById("chat-active");
  const chatCharacterNameEl = document.getElementById("chat-character-name");
  const messagesEl = document.getElementById("messages");
  const textInputEl = document.getElementById("text-input");
  const sendBtnEl = document.getElementById("send-btn");
  const langToggleEl = document.getElementById("lang-toggle");

  const profileModalEl = document.getElementById("profile-modal");
  const profileAvatarPreviewEl = document.getElementById(
    "profile-avatar-preview",
  );
  const avatarInputEl = document.getElementById("avatar-input");
  const nameInputEl = document.getElementById("name-input");
  const profileSaveBtnEl = document.getElementById("profile-save-btn");
  const profileCancelBtnEl = document.getElementById("profile-cancel-btn");
  const settingsBtnEl = document.getElementById("settings-btn");
  const myProfileEl = document.getElementById("my-profile");

  function getCharacterAvatar(charOrId) {
    const id =
      typeof charOrId === "string" ? charOrId : charOrId && charOrId.id;
    if (!id) return "🙂";
    return CHARACTER_AVATARS[id] || (id.charAt(0) || "🙂").toUpperCase();
  }

  function formatMessageTime(date = new Date()) {
    return new Intl.DateTimeFormat(undefined, {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
      .format(date)
      .toLowerCase();
  }

  function updateChatHeader(char) {
    chatCharacterNameEl.innerHTML = "";

    const avatar = document.createElement("span");
    avatar.className = "chat-header-avatar";
    avatar.textContent = getCharacterAvatar(char);

    const name = document.createElement("span");
    name.className = "chat-header-name";
    name.textContent = (char && char.name) || "";

    chatCharacterNameEl.appendChild(avatar);
    chatCharacterNameEl.appendChild(name);
  }

  /* ---------- Profile modal wiring ---------- */
  let pendingAvatarDataUrl = null;

  function openProfileModal() {
    nameInputEl.value = profile.name || "";
    profileAvatarPreviewEl.src = profile.avatar || DEFAULT_AVATAR;
    pendingAvatarDataUrl = null;
    profileModalEl.classList.remove("hidden");
  }

  function closeProfileModal() {
    profileModalEl.classList.add("hidden");
  }

  settingsBtnEl.addEventListener("click", openProfileModal);
  myProfileEl.addEventListener("click", openProfileModal);
  profileCancelBtnEl.addEventListener("click", closeProfileModal);

  avatarInputEl.addEventListener("change", () => {
    const file = avatarInputEl.files && avatarInputEl.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      pendingAvatarDataUrl = reader.result;
      profileAvatarPreviewEl.src = pendingAvatarDataUrl;
    };
    reader.readAsDataURL(file);
  });

  profileSaveBtnEl.addEventListener("click", () => {
    const newName = nameInputEl.value.trim() || "You";
    profile = {
      name: newName,
      avatar: pendingAvatarDataUrl || profile.avatar || DEFAULT_AVATAR,
    };
    saveProfile(profile);
    renderProfile();
    closeProfileModal();
  });

  /* ---------- Load characters ---------- */
  async function loadCharacters() {
    try {
      const res = await fetch("/api/characters");
      const data = await res.json();
      characters = (data && data.characters) || [];
      renderContactList();
    } catch (e) {
      contactListEl.innerHTML =
        '<div style="padding:16px;color:#888;font-size:13px;">Couldn\'t load characters.</div>';
    }
  }

  function renderContactList() {
    contactListEl.innerHTML = "";
    characters.forEach((char) => {
      const item = document.createElement("div");
      item.className = "contact-item";
      item.dataset.id = char.id;

      const avatar = document.createElement("div");
      avatar.className = "contact-avatar";
      avatar.textContent = getCharacterAvatar(char);

      const meta = document.createElement("div");
      meta.className = "contact-meta";

      const name = document.createElement("div");
      name.className = "contact-name";
      name.textContent = char.name;

      const sub = document.createElement("div");
      sub.className = "contact-sub";
      sub.textContent = char.has_voice ? "Voice enabled" : "Text only";

      meta.appendChild(name);
      meta.appendChild(sub);
      item.appendChild(avatar);
      item.appendChild(meta);

      item.addEventListener("click", () => selectCharacter(char));
      contactListEl.appendChild(item);
    });
  }

  async function selectCharacter(char) {
    activeCharacter = char;
    stopCurrentAudio();

    document.querySelectorAll(".contact-item").forEach((el) => {
      el.classList.toggle("active", el.dataset.id === char.id);
    });

    emptyStateEl.classList.add("hidden");
    chatActiveEl.classList.remove("hidden");
    updateChatHeader(char);
    messagesEl.innerHTML = "";

    await restoreHistory(char);

    textInputEl.focus();
  }

  async function restoreHistory(char) {
    try {
      const url =
        "/api/chat/history?session_id=" +
        encodeURIComponent(sessionId) +
        "&character_id=" +
        encodeURIComponent(char.id);
      const res = await fetch(url);
      if (!res.ok) return;
      const data = await res.json();
      const hasVoice = !!char.has_voice;

      data.messages.forEach((msg) => {
        if (msg.role === "user") {
          appendUserBubble(msg.content);
        } else {
          appendCharacterBubble(msg.content, hasVoice);
        }
      });
    } catch (e) {
      // History restore failed — not fatal, chat just starts empty
    }
  }

  /* ---------- Language toggle ---------- */
  langToggleEl.addEventListener("click", () => {
    language = language === "en" ? "hi" : "en";
    langToggleEl.textContent = language.toUpperCase();
  });
  langToggleEl.textContent = language.toUpperCase();

  /* ---------- Sending messages ---------- */
  sendBtnEl.addEventListener("click", sendMessage);
  textInputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  async function sendMessage() {
    if (sending) return;
    const text = textInputEl.value.trim();
    if (!text || !activeCharacter) return;

    setSending(true);
    appendUserBubble(text);
    textInputEl.value = "";

    const typingRow = appendTypingIndicator();

    try {
      const res = await fetch("/api/chat/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          character_id: activeCharacter.id,
          user_name: profile.name || "You",
          text: text,
          language: language,
        }),
      });

      if (!res.ok) throw new Error("bad status " + res.status);
      const data = await res.json();
      removeTypingIndicator(typingRow);

      const bubbles =
        data.reply_bubbles && data.reply_bubbles.length
          ? data.reply_bubbles
          : [data.reply || "..."];

      await revealBubblesSequentially(bubbles, !!data.auto_voice);
    } catch (e) {
      removeTypingIndicator(typingRow);
      appendCharacterBubble("(connection hiccup — try again)", false);
    } finally {
      setSending(false);
    }
  }

  function setSending(state) {
    sending = state;
    sendBtnEl.disabled = state;
  }

  /* ---------- Bubble rendering ---------- */
  function appendUserBubble(text) {
    const row = document.createElement("div");
    row.className = "bubble-row user";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const span = document.createElement("span");
    span.className = "bubble-text";
    span.textContent = text;
    bubble.appendChild(span);

    const meta = document.createElement("div");
    meta.className = "bubble-meta";

    const time = document.createElement("span");
    time.className = "bubble-time";
    time.textContent = formatMessageTime();

    const receipt = document.createElement("span");
    receipt.className = "bubble-receipt";
    receipt.textContent = "✓✓";

    meta.appendChild(time);
    meta.appendChild(receipt);
    bubble.appendChild(meta);

    row.appendChild(bubble);
    messagesEl.appendChild(row);
    scrollToBottom();
  }

  function appendCharacterBubble(text, withVoice) {
    const row = document.createElement("div");
    row.className = "bubble-row character";

    const avatar = document.createElement("div");
    avatar.className = "bubble-avatar";
    avatar.textContent = getCharacterAvatar(activeCharacter);

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const span = document.createElement("span");
    span.className = "bubble-text";
    span.textContent = text;
    bubble.appendChild(span);

    const meta = document.createElement("div");
    meta.className = "bubble-meta";

    const time = document.createElement("span");
    time.className = "bubble-time";
    time.textContent = formatMessageTime();
    meta.appendChild(time);
    bubble.appendChild(meta);

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesEl.appendChild(row);

    let voiceBtn = null;
    if (withVoice) {
      const voiceRow = document.createElement("div");
      voiceRow.className = "bubble-row character voice-row";

      const voiceAvatar = document.createElement("div");
      voiceAvatar.className = "bubble-avatar";
      voiceAvatar.textContent = getCharacterAvatar(activeCharacter);

      const voiceBubble = document.createElement("div");
      voiceBubble.className = "voice-bubble";

      voiceBtn = document.createElement("button");
      voiceBtn.className = "voice-icon";
      voiceBtn.dataset.voiceLabel = "▶─────────────── 0:07";
      voiceBtn.textContent = voiceBtn.dataset.voiceLabel;
      voiceBtn.title = "Play voice";
      voiceBtn.addEventListener("click", () => {
        playVoice(activeCharacter.id, text, voiceBtn);
      });

      const voiceMeta = document.createElement("div");
      voiceMeta.className = "bubble-meta";
      const voiceTime = document.createElement("span");
      voiceTime.className = "bubble-time";
      voiceTime.textContent = formatMessageTime();
      voiceMeta.appendChild(voiceTime);

      voiceBubble.appendChild(voiceBtn);
      voiceBubble.appendChild(voiceMeta);
      voiceRow.appendChild(voiceAvatar);
      voiceRow.appendChild(voiceBubble);
      messagesEl.appendChild(voiceRow);
    }

    scrollToBottom();
    return voiceBtn;
  }

  // Simplified typing indicator — immediate append, no internal delay
  function appendTypingIndicator() {
    const row = document.createElement("div");
    row.className = "typing-row";

    const avatar = document.createElement("div");
    avatar.className = "bubble-avatar";
    avatar.textContent = getCharacterAvatar(activeCharacter);

    const bubble = document.createElement("div");
    bubble.className = "typing-bubble";

    const dots = document.createElement("div");
    dots.className = "typing-dots";
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.className = "typing-dot";
      dots.appendChild(dot);
    }

    const label = document.createElement("span");
    label.className = "typing-text";
    label.textContent = `${(activeCharacter && activeCharacter.name) || "Character"} is typing...`;

    const meta = document.createElement("div");
    meta.className = "bubble-meta typing-meta";
    meta.textContent = formatMessageTime();

    bubble.appendChild(dots);
    bubble.appendChild(label);
    bubble.appendChild(meta);

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesEl.appendChild(row);
    scrollToBottom();

    return row;
  }

  function removeTypingIndicator(row) {
    if (row && row.parentNode) row.parentNode.removeChild(row);
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /* ---------- Sequential bubble reveal ---------- */
  // Restore sane pacing — one delay per bubble (700-1200ms)
  async function revealBubblesSequentially(bubbles, autoVoice) {
    const hasVoice = !!(activeCharacter && activeCharacter.has_voice);
    let lastVoiceBtn = null;
    let lastText = null;

    for (let i = 0; i < bubbles.length; i++) {
      const typingRow = appendTypingIndicator();
      const delay = 700 + Math.random() * 500; // 700-1200ms — feels natural, not slow
      await wait(delay);
      removeTypingIndicator(typingRow);

      const btn = appendCharacterBubble(bubbles[i], hasVoice);
      lastVoiceBtn = btn;
      lastText = bubbles[i];
    }

    if (autoVoice && hasVoice && lastVoiceBtn && lastText != null) {
      playVoice(activeCharacter.id, lastText, lastVoiceBtn);
    }
  }

  /* ---------- Voice playback ---------- */

  function stopCurrentAudio() {
    if (currentAudio) {
      try {
        currentAudio.pause();
      } catch (e) {
        /* ignore */
      }
      currentAudio = null;
    }
    if (currentPlayingBtn) {
      setIconState(currentPlayingBtn, "idle");
      currentPlayingBtn = null;
    }
  }

  function setIconState(btn, state) {
    if (!btn) return;
    btn.classList.remove("loading", "playing");
    if (state === "loading") {
      btn.textContent = "⏳";
      btn.classList.add("loading");
    } else if (state === "playing") {
      btn.textContent = "⏸";
      btn.classList.add("playing");
    } else {
      btn.textContent = btn.dataset.voiceLabel || "▶─────────────── 0:07";
    }
  }

  function fillerFileFor(characterId, index) {
    const suffix = language === "en" ? "e" + index : String(index);
    return `audio/${characterId}_filler_${suffix}.mp3`;
  }

  function appendFillerBubble(characterId) {
    try {
      const row = document.createElement("div");
      row.className = "bubble-row character filler-row";

      const avatar = document.createElement("div");
      avatar.className = "bubble-avatar";
      avatar.textContent = getCharacterAvatar(characterId);

      const bubble = document.createElement("div");
      bubble.className = "bubble filler-bubble";

      const span = document.createElement("span");
      span.className = "bubble-text filler-text";
      span.textContent = "(audio)…";
      bubble.appendChild(span);

      const meta = document.createElement("div");
      meta.className = "bubble-meta";
      const time = document.createElement("span");
      time.className = "bubble-time";
      time.textContent = formatMessageTime();
      meta.appendChild(time);
      bubble.appendChild(meta);

      row.appendChild(avatar);
      row.appendChild(bubble);
      messagesEl.appendChild(row);
      scrollToBottom();
      return row;
    } catch (e) {
      return null;
    }
  }

  async function playVoice(characterId, text, btn) {
    const myTicket = ++voiceTicket;
    setIconState(btn, "loading");

    const cacheKey = `${characterId}::${text}`;
    let fillerAudio = null;
    let fillerTimer = null;
    let fillerStarted = false;
    let fillerRow = null;

    // Schedule filler audio if the real response is slow. Delay increased to 2-4s.
    const fillerDelay = 2000 + Math.floor(Math.random() * 2000); // 2000-4000ms
    fillerTimer = setTimeout(() => {
      if (myTicket !== voiceTicket) return; // superseded already
      const available = FILLER_INDICES[characterId] || [1, 2];
      const idx = available[Math.floor(Math.random() * available.length)];
      const fillerSrc = fillerFileFor(characterId, idx);
      fillerAudio = new Audio(fillerSrc);

      // Append a subtle filler bubble so filler audio appears as a separate message.
      try {
        fillerRow = appendFillerBubble(characterId);
      } catch (e) {
        /* ignore UI failures */
      }

      fillerAudio.play().catch(() => {
        /* filler file may not exist locally — ignore */
      });
      fillerStarted = true;
    }, fillerDelay);

    function cancelFiller() {
      clearTimeout(fillerTimer);
      if (fillerAudio) {
        try {
          fillerAudio.pause();
        } catch (e) {
          /* ignore */
        }
        fillerAudio = null;
      }
      // mark filler UI as ended (optional) — leave it visible as a separate message
      if (fillerRow && fillerRow.parentNode) {
        fillerRow.classList.add("filler-ended");
      }
    }

    let blobUrl = audioCache.get(cacheKey);

    if (!blobUrl) {
      try {
        const url =
          "/api/voice/stream?character_id=" +
          encodeURIComponent(characterId) +
          "&text=" +
          encodeURIComponent(text);
        const res = await fetch(url, { method: "GET" });
        if (!res.ok) throw new Error("voice fetch failed " + res.status);
        const blob = await res.blob();
        blobUrl = URL.createObjectURL(blob);
        audioCache.set(cacheKey, blobUrl);
      } catch (e) {
        cancelFiller();
        // Only reset this button if it's still the most recent request for it.
        setIconState(btn, "idle");
        return; // silent fallback to text-only
      }
    }

    cancelFiller();

    // Race check: only the most recent request may actually play.
    if (myTicket !== voiceTicket) {
      return;
    }

    stopCurrentAudio();

    const audio = new Audio(blobUrl);
    currentAudio = audio;
    currentPlayingBtn = btn;
    setIconState(btn, "playing");

    audio.addEventListener("ended", () => {
      if (currentAudio === audio) {
        setIconState(btn, "idle");
        currentAudio = null;
        currentPlayingBtn = null;
      }
    });

    audio.addEventListener("error", () => {
      if (currentAudio === audio) {
        setIconState(btn, "idle");
        currentAudio = null;
        currentPlayingBtn = null;
      }
    });

    audio.play().catch(() => {
      setIconState(btn, "idle");
      if (currentAudio === audio) {
        currentAudio = null;
        currentPlayingBtn = null;
      }
    });
  }

  /* ---------- Init ---------- */
  renderProfile();
  loadCharacters();
})();
