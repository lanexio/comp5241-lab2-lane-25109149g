


document.addEventListener("DOMContentLoaded", () => {
    const noteTitleInput = document.getElementById("note-title");
    const noteContentInput = document.getElementById("note-content");
    const saveNoteButton = document.getElementById("save-note");
    const newNoteButton = document.getElementById("new-note");
    const noteListDiv = document.getElementById("note-list");
    const searchInput = document.getElementById("search-input");
    const searchButton = document.getElementById("search-button");
    const noteIdInput = document.getElementById("note-id");
    const translateButton = document.getElementById("translate-button");

    let currentNoteId = null;
    let autoSaveTimeout;

    const API_BASE_URL = "/api";

    // Helper to collect texts to translate and map them back
    function collectTextsForTranslation() {
        const items = [];
        // Page title
        const pageTitle = document.querySelector('h1')?.textContent || '';
        items.push({ id: 'page-title', text: pageTitle });

        // Inputs and placeholders
        items.push({ id: 'note-title-placeholder', text: noteTitleInput.placeholder || '' });
        items.push({ id: 'note-content-placeholder', text: noteContentInput.placeholder || '' });

        // Current loaded note (title and content)
        items.push({ id: 'current-note-title', text: noteTitleInput.value || '' });
        items.push({ id: 'current-note-content', text: noteContentInput.value || '' });

        // Note list items (titles and excerpts)
        const noteItems = Array.from(document.querySelectorAll('.note-item'));
        noteItems.forEach((el, idx) => {
            const h3 = el.querySelector('h3');
            const p = el.querySelector('p');
            if (h3) items.push({ id: `note-${idx}-title`, text: h3.textContent || '' });
            if (p) items.push({ id: `note-${idx}-excerpt`, text: p.textContent || '' });
        });

        return items;
    }

    async function applyTranslations(translations, items) {
        const map = {};
        items.forEach((it, i) => map[it.id] = translations[i] || '');

        // Apply page title
        if (map['page-title']) document.querySelector('h1').textContent = map['page-title'];

        // Apply placeholders
        if (map['note-title-placeholder']) noteTitleInput.placeholder = map['note-title-placeholder'];
        if (map['note-content-placeholder']) noteContentInput.placeholder = map['note-content-placeholder'];

        // Apply current note contents (only if non-empty translations)
        if (map['current-note-title']) noteTitleInput.value = map['current-note-title'];
        if (map['current-note-content']) noteContentInput.value = map['current-note-content'];

        // Apply note list translations
        const noteItems = Array.from(document.querySelectorAll('.note-item'));
        noteItems.forEach((el, idx) => {
            const h3 = el.querySelector('h3');
            const p = el.querySelector('p');
            const titleKey = `note-${idx}-title`;
            const excerptKey = `note-${idx}-excerpt`;
            if (h3 && map[titleKey]) h3.textContent = map[titleKey];
            if (p && map[excerptKey]) p.textContent = map[excerptKey];
        });
    }

    // Client-side pagination state
    let notesCache = [];
    let currentPage = 1;
    const pageSize = 3;

    // Render a page of notes
    function renderNotesPage(page = 1) {
        noteListDiv.innerHTML = "";
        const start = (page - 1) * pageSize;
        const pageItems = notesCache.slice(start, start + pageSize);
        pageItems.forEach(note => {
            const noteItem = document.createElement("div");
            noteItem.classList.add("note-item");
            noteItem.dataset.id = note.id;
            noteItem.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.content.substring(0, 100)}...</p>
                <small>${new Date(note.timestamp).toLocaleString()}</small>
                <div style="margin-top:8px; display:flex; gap:8px;">
                    <button class="action-button open-note">Open</button>
                    <button class="action-button delete-note">Delete</button>
                </div>
            `;
            noteItem.querySelector(".open-note").addEventListener("click", () => loadNoteForEdit(note.id));
            noteItem.querySelector("h3").addEventListener("click", () => loadNoteForEdit(note.id));
            noteItem.querySelector("p").addEventListener("click", () => loadNoteForEdit(note.id));
            noteItem.querySelector(".delete-note").addEventListener("click", (e) => {
                e.stopPropagation();
                deleteNote(note.id);
            });
            noteListDiv.appendChild(noteItem);
        });
        renderPaginationControls();
    }

    function renderPaginationControls() {
        const totalPages = Math.max(1, Math.ceil(notesCache.length / pageSize));
        const paginationDiv = document.getElementById('pagination');
        if (!paginationDiv) return;
        paginationDiv.innerHTML = '';

        const prev = document.createElement('button');
        prev.className = 'action-button';
        prev.textContent = 'Previous';
        prev.disabled = currentPage === 1;
        prev.addEventListener('click', () => { if (currentPage > 1) { currentPage -= 1; renderNotesPage(currentPage); } });
        paginationDiv.appendChild(prev);

        // page numbers
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.className = 'action-button';
            btn.textContent = i;
            if (i === currentPage) btn.style.opacity = '0.8';
            btn.addEventListener('click', () => { currentPage = i; renderNotesPage(currentPage); });
            paginationDiv.appendChild(btn);
        }

        const next = document.createElement('button');
        next.className = 'action-button';
        next.textContent = 'Next';
        next.disabled = currentPage === totalPages;
        next.addEventListener('click', () => { if (currentPage < totalPages) { currentPage += 1; renderNotesPage(currentPage); } });
        paginationDiv.appendChild(next);

        // page info
        const info = document.createElement('div');
        info.style.marginLeft = '12px';
        info.style.alignSelf = 'center';
        info.style.color = 'var(--muted-faint)';
        info.textContent = `当前第 ${currentPage} 页，共 ${totalPages} 页`;
        paginationDiv.appendChild(info);
    }

    // Function to fetch notes and populate cache (supports optional search)
    async function fetchNotes(query = "") {
        noteListDiv.innerHTML = "";
        let url = `${API_BASE_URL}/notes`;
        if (query) {
            url = `${API_BASE_URL}/notes/search?q=${encodeURIComponent(query)}`;
        }
        const response = await fetch(url);
        const data = await response.json();
        notesCache = data.notes || [];
        currentPage = 1;
        renderNotesPage(currentPage);
    }

    // Function to load a note for editing
    async function loadNoteForEdit(id) {
        const response = await fetch(`${API_BASE_URL}/notes/${id}`);
        const note = await response.json();
        noteIdInput.value = note.id;
        noteTitleInput.value = note.title;
        noteContentInput.value = note.content;
        currentNoteId = note.id;
        saveNoteButton.textContent = "Update Note";
        newNoteButton.style.display = "inline-block";
    }

    // Function to save or update a note
    async function saveNote() {
        const title = noteTitleInput.value;
        const content = noteContentInput.value;

        if (!title) {
            alert("Note title cannot be empty.");
            return;
        }

        const noteData = { title, content };
        let response;

        if (currentNoteId) {
            // Update existing note
            response = await fetch(`${API_BASE_URL}/notes/${currentNoteId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(noteData),
            });
        } else {
            // Create new note
            response = await fetch(`${API_BASE_URL}/notes`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(noteData),
            });
        }

        if (response.ok) {
            clearForm();
            fetchNotes();
        } else {
            alert("Failed to save note.");
        }
    }

    // Function to delete a note
    async function deleteNote(id) {
        if (confirm("Are you sure you want to delete this note?")) {
            const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
                method: "DELETE",
            });
            if (response.ok) {
                clearForm();
                fetchNotes();
            } else {
                alert("Failed to delete note.");
            }
        }
    }

    // Function to clear the form
    function clearForm() {
        noteIdInput.value = "";
        noteTitleInput.value = "";
        noteContentInput.value = "";
        currentNoteId = null;
        saveNoteButton.textContent = "Save Note";
        newNoteButton.style.display = "none";
    }

    // Auto-save functionality
    function setupAutoSave() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            if (noteTitleInput.value || noteContentInput.value) {
                saveNote();
            }
        }, 30000); // Auto-save every 30 seconds
    }

    // Event Listeners
    saveNoteButton.addEventListener("click", saveNote);
    newNoteButton.addEventListener("click", clearForm);
    searchButton.addEventListener("click", () => fetchNotes(searchInput.value));
    searchInput.addEventListener("keyup", (e) => {
        if (e.key === "Enter") {
            fetchNotes(searchInput.value);
        }
    });

    noteTitleInput.addEventListener("input", setupAutoSave);
    noteContentInput.addEventListener("input", setupAutoSave);

    // Translate button handler: only translate left-side title and content
    if (translateButton) {
        translateButton.addEventListener('click', async () => {
            translateButton.disabled = true;
            const originalText = { title: noteTitleInput.value || noteTitleInput.placeholder || '', content: noteContentInput.value || noteContentInput.placeholder || '' };
            translateButton.textContent = 'Translating...';
            try {
                const items = [{ id: 'title', text: originalText.title }, { id: 'content', text: originalText.content }];
                const resp = await fetch(`${API_BASE_URL}/translate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ items }),
                });
                const data = await resp.json();
                if (resp.ok && data.translations && Array.isArray(data.translations)) {
                    if (data.translations[0]) noteTitleInput.value = data.translations[0];
                    if (data.translations[1]) noteContentInput.value = data.translations[1];
                } else {
                    console.error('Translation failed', data);
                    alert('Translation failed. See console for details.');
                }
            } catch (e) {
                console.error(e);
                alert('Translation request failed.');
            } finally {
                translateButton.disabled = false;
                translateButton.textContent = 'Translate 🪄';
            }
        });
    }

    // Initial load
    fetchNotes();

    // AI Generate Note UI
    const aiButton = document.getElementById('ai-note-button');
    const aiPanel = document.getElementById('ai-panel');
    const aiDesc = document.getElementById('ai-desc');
    const aiLang = document.getElementById('ai-lang');
    const aiGenerate = document.getElementById('ai-generate');
    const aiCancel = document.getElementById('ai-cancel');
    const aiCancel2 = document.getElementById('ai-cancel-2');
    const aiPreviewTitle = document.getElementById('ai-title');
    const aiPreviewContent = document.getElementById('ai-content');
    const aiTagsDiv = document.getElementById('ai-tags');
    const aiSave = document.getElementById('ai-save');

    const aiOverlay = document.getElementById('ai-modal-overlay');
    function openAiPanel() {
        aiPanel.style.display = 'flex';
        if (aiOverlay) aiOverlay.style.display = 'block';
    }
    function closeAiPanel() {
        aiPanel.style.display = 'none';
        if (aiOverlay) aiOverlay.style.display = 'none';
        aiPreviewTitle.textContent = '';
        aiPreviewContent.textContent = '';
        aiTagsDiv.innerHTML = '';
    }

    // Close on overlay click or Esc
    if (aiOverlay) {
        aiOverlay.addEventListener('click', closeAiPanel);
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAiPanel();
    });

    aiButton.addEventListener('click', openAiPanel);
    aiCancel.addEventListener('click', closeAiPanel);
    aiCancel2.addEventListener('click', closeAiPanel);

    aiGenerate.addEventListener('click', async () => {
        aiGenerate.disabled = true;
        aiGenerate.textContent = 'Generating...';
        const payload = { description: aiDesc.value, language: aiLang.value };
        try {
            const resp = await fetch(`${API_BASE_URL}/generate_note`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await resp.json();
            if (resp.ok && data.title) {
                aiPreviewTitle.textContent = data.title;
                aiPreviewContent.textContent = data.content;
                aiTagsDiv.innerHTML = '';
                (data.tags || []).forEach(t => {
                    const span = document.createElement('span');
                    span.className = 'ai-tag';
                    span.textContent = t;
                    aiTagsDiv.appendChild(span);
                });
            } else {
                alert('AI generation failed. See console for details.');
                console.error(data);
            }
        } catch (e) {
            console.error(e);
            alert('AI generation request failed.');
        } finally {
            aiGenerate.disabled = false;
            aiGenerate.textContent = 'Generate';
        }
    });

    aiSave.addEventListener('click', async () => {
        const title = aiPreviewTitle.textContent;
        const content = aiPreviewContent.textContent;
        if (!title) { alert('No generated note to save'); return; }
        // Reuse existing saveNote logic: populate inputs and call saveNote()
        noteTitleInput.value = title;
        noteContentInput.value = content;
        // ensure currentNoteId is cleared so saveNote creates a new note
        currentNoteId = null;
        await saveNote();
        closeAiPanel();
    });
});

