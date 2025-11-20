/**
 * Document Management System
 * Handles file uploads, document listing, and management
 */

const API_BASE_URL = 'http://localhost:8002';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadDocuments();
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // File upload
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const uploadArea = document.getElementById('uploadArea');

    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // URL upload
    document.getElementById('urlUploadBtn').addEventListener('click', handleUrlUpload);

    // Refresh and clear
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadStats();
        loadDocuments();
    });

    document.getElementById('clearAllBtn').addEventListener('click', handleClearAll);
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        document.getElementById('totalDocs').textContent = data.vector_store_stats.total_documents;
        document.getElementById('vectorCount').textContent = data.vector_store_stats.total_vectors;
        document.getElementById('indexType').textContent = data.vector_store_stats.index_type;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load documents list
async function loadDocuments() {
    const docsList = document.getElementById('documentsList');
    docsList.innerHTML = '<div class="loading">Loading documents...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/documents/list`);
        const data = await response.json();

        if (data.total === 0) {
            docsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <div class="empty-state-text">No documents yet</div>
                    <div class="empty-state-hint">Upload your first document to get started</div>
                </div>
            `;
            return;
        }

        // Display documents
        docsList.innerHTML = '';
        data.documents.forEach(doc => {
            const docElement = createDocumentElement(doc);
            docsList.appendChild(docElement);
        });

    } catch (error) {
        console.error('Error loading documents:', error);
        docsList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <div class="empty-state-text">Error loading documents</div>
                <div class="empty-state-hint">${error.message}</div>
            </div>
        `;
    }
}

// Create document element
function createDocumentElement(doc) {
    const div = document.createElement('div');
    div.className = 'document-item';

    const icon = getFileIcon(doc.type);
    const typeLabel = doc.type ? doc.type.toUpperCase() : 'DOC';

    div.innerHTML = `
        <div class="document-header">
            <div class="document-title">
                <span class="document-icon">${icon}</span>
                <div>
                    <div class="document-name">${escapeHtml(doc.filename)}</div>
                </div>
            </div>
            <div class="document-actions">
                <button class="btn-icon btn-delete" onclick="deleteDocument(${doc.id})" title="Delete">
                    🗑️
                </button>
            </div>
        </div>
        <div class="document-meta">
            <span class="meta-item">
                <span>📦</span> ${typeLabel}
            </span>
            <span class="meta-item">
                <span>📏</span> ${formatBytes(doc.content_length)}
            </span>
            <span class="meta-item">
                <span>🏷️</span> ${escapeHtml(doc.category)}
            </span>
            <span class="meta-item">
                <span>🆔</span> ID: ${doc.id}
            </span>
        </div>
        <div class="document-preview">
            ${escapeHtml(doc.content_preview)}
        </div>
    `;

    return div;
}

// Get file icon based on type
function getFileIcon(type) {
    const icons = {
        'pdf': '📄',
        'txt': '📝',
        'html': '🌐',
        'md': '📋',
        'website': '🌐'
    };
    return icons[type?.toLowerCase()] || '📄';
}

// Format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle file selection
async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        await uploadFile(file);
    }
}

// Drag and drop handlers
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

async function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file) {
        await uploadFile(file);
    }
}

// Upload file
async function uploadFile(file) {
    const progressDiv = document.getElementById('uploadProgress');
    const resultDiv = document.getElementById('uploadResult');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    // Show progress
    progressDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading...';

    try {
        // Simulate progress (since we can't track actual upload progress easily)
        progressFill.style.width = '30%';
        progressText.textContent = 'Uploading file...';

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        progressFill.style.width = '70%';
        progressText.textContent = 'Processing document...';

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();

        // Complete
        progressFill.style.width = '100%';
        progressText.textContent = 'Complete!';

        // Show success message
        setTimeout(() => {
            progressDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.className = 'upload-result success';
            resultDiv.innerHTML = `
                ✅ <strong>Success!</strong><br>
                ${data.message}<br>
                <small>${data.chunks_created} chunks created • ${data.total_documents} total documents</small>
            `;

            // Refresh documents list
            loadStats();
            loadDocuments();

            // Clear file input
            document.getElementById('fileInput').value = '';
        }, 500);

    } catch (error) {
        console.error('Upload error:', error);
        progressDiv.style.display = 'none';
        resultDiv.style.display = 'block';
        resultDiv.className = 'upload-result error';
        resultDiv.innerHTML = `
            ❌ <strong>Error:</strong> ${error.message}
        `;
    }
}

// Handle URL upload
async function handleUrlUpload() {
    const urlInput = document.getElementById('urlInput');
    const urlResultDiv = document.getElementById('urlResult');
    const urlUploadBtn = document.getElementById('urlUploadBtn');
    const url = urlInput.value.trim();

    if (!url) {
        alert('Please enter a URL');
        return;
    }

    // Validate URL
    try {
        new URL(url);
    } catch (e) {
        alert('Please enter a valid URL');
        return;
    }

    // Show loading state
    urlResultDiv.style.display = 'block';
    urlResultDiv.className = 'url-result';
    urlResultDiv.innerHTML = '⏳ Loading content from URL...';
    urlUploadBtn.disabled = true;
    urlUploadBtn.textContent = 'Loading...';

    try {
        const response = await fetch(`${API_BASE_URL}/documents/upload-url?url=${encodeURIComponent(url)}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load URL');
        }

        const data = await response.json();

        // Show success
        urlResultDiv.className = 'url-result success';
        urlResultDiv.innerHTML = `
            ✅ <strong>Success!</strong><br>
            ${data.message}<br>
            <small>${data.chunks_created} chunks created • ${data.total_documents} total documents</small>
        `;

        // Refresh
        loadStats();
        loadDocuments();

        // Clear input
        urlInput.value = '';

    } catch (error) {
        console.error('URL upload error:', error);
        urlResultDiv.className = 'url-result error';
        urlResultDiv.innerHTML = `
            ❌ <strong>Error:</strong> ${error.message}
        `;
    } finally {
        urlUploadBtn.disabled = false;
        urlUploadBtn.textContent = 'Load URL';
    }
}

// Delete document
async function deleteDocument(docId) {
    if (!confirm(`Are you sure you want to delete document #${docId}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/documents/${docId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Delete failed');
        }

        const data = await response.json();
        alert(`✅ ${data.message}\n${data.remaining_documents} documents remaining`);

        // Refresh
        loadStats();
        loadDocuments();

    } catch (error) {
        console.error('Delete error:', error);
        alert(`❌ Error: ${error.message}`);
    }
}

// Clear all documents
async function handleClearAll() {
    if (!confirm('⚠️ Are you sure you want to delete ALL documents? This action cannot be undone.')) {
        return;
    }

    if (!confirm('This will permanently delete all documents from the knowledge base. Continue?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/documents/clear`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Clear failed');
        }

        const data = await response.json();
        alert(`✅ ${data.message}`);

        // Refresh
        loadStats();
        loadDocuments();

    } catch (error) {
        console.error('Clear error:', error);
        alert(`❌ Error: ${error.message}`);
    }
}

// Make deleteDocument available globally
window.deleteDocument = deleteDocument;
