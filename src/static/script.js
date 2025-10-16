
document.addEventListener("DOMContentLoaded", () => {
    const noteTitleInput = document.getElementById("note-title");
    const noteContentInput = document.getElementById("note-content");
    const saveNoteButton = document.getElementById("save-note");
    const newNoteButton = document.getElementById("new-note");
    const noteListDiv = document.getElementById("note-list");
    const searchInput = document.getElementById("search-input");
    const searchButton = document.getElementById("search-button");
    const noteIdInput = document.getElementById("note-id");

    let currentNoteId = null;
    let autoSaveTimeout;

    const API_BASE_URL = "/api";

    // Function to fetch and display notes
    async function fetchNotes(query = "") {
        noteListDiv.innerHTML = "";
        let url = `${API_BASE_URL}/notes`;
        if (query) {
            url = `${API_BASE_URL}/notes/search?q=${encodeURIComponent(query)}`;
        }
        const response = await fetch(url);
        const data = await response.json();
        data.notes.forEach(note => {
            const noteItem = document.createElement("div");
            noteItem.classList.add("note-item");
            noteItem.dataset.id = note.id;
            noteItem.innerHTML = `
                <h3>${note.title}</h3>
                <p>${note.content.substring(0, 100)}...</p>
                <small>${new Date(note.timestamp).toLocaleString()}</small>
                <button class="delete-note">Delete</button>
            `;
            noteItem.querySelector("h3").addEventListener("click", () => loadNoteForEdit(note.id));
            noteItem.querySelector("p").addEventListener("click", () => loadNoteForEdit(note.id));
            noteItem.querySelector(".delete-note").addEventListener("click", (e) => {
                e.stopPropagation();
                deleteNote(note.id);
            });
            noteListDiv.appendChild(noteItem);
        });
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

    // Initial load
    fetchNotes();
});

