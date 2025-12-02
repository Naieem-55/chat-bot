// Citation Modal Functionality

// Show citation modal with full context
function showCitationModal(source) {
    const modal = document.getElementById('citationModal');
    const overlay = document.getElementById('citationModalOverlay');
    const body = document.getElementById('citationModalBody');

    // Build modal content
    const sourceName = source.category || extractFilename(source.source);
    const fullText = source.full_text || source.excerpt || 'No content available';

    body.innerHTML = `
        <div class="citation-source-info">
            <div><strong>Source:</strong> ${sourceName}</div>
            <div><strong>Relevance:</strong> ${Math.round(source.relevance_score * 100)}%</div>
            ${source.category ? `<div><strong>Category:</strong> ${source.category}</div>` : ''}
            ${source.chunk_id ? `<div><strong>Chunk ID:</strong> ${source.chunk_id}</div>` : ''}
        </div>
        <div class="citation-full-text">${escapeHtml(fullText)}</div>
    `;

    // Show modal
    modal.style.display = 'flex';
    overlay.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Close citation modal
function closeCitationModal() {
    const modal = document.getElementById('citationModal');
    const overlay = document.getElementById('citationModalOverlay');

    modal.style.display = 'none';
    overlay.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Create enhanced source item with excerpt and clickable
function createEnhancedSourceItem(source, index) {
    const sourceItem = document.createElement('div');
    sourceItem.className = 'source-item';

    const emoji = getSourceEmoji(source.source, source.category);
    const relevance = Math.round(source.relevance_score * 100);
    const isWebSource = source.is_web_result || source.source.startsWith('http');
    const sourceName = source.title || source.category || extractFilename(source.source);
    const excerpt = source.excerpt || 'No preview available';

    if (isWebSource) {
        // Web source with clickable link
        sourceItem.innerHTML = `
            <div class="source-header">
                <span class="source-emoji">${emoji}</span>
                <a href="${source.source}" target="_blank" rel="noopener noreferrer" class="source-link" onclick="event.stopPropagation();">
                    ${sourceName}
                    <span class="source-link-icon">↗</span>
                </a>
                <span class="source-relevance" title="Relevance score">${relevance}%</span>
            </div>
            <a href="${source.source}" target="_blank" rel="noopener noreferrer" class="source-url" onclick="event.stopPropagation();">${source.source}</a>
            ${excerpt !== 'No preview available' ? `<div class="source-excerpt">"${escapeHtml(excerpt)}"</div>` : ''}
        `;
    } else {
        // Local source
        sourceItem.innerHTML = `
            <div class="source-header">
                <span class="source-emoji">${emoji}</span>
                <span class="source-name">${sourceName}</span>
                <span class="source-relevance" title="Relevance score">${relevance}%</span>
            </div>
            <div class="source-excerpt">"${escapeHtml(excerpt)}"</div>
            <div class="source-view-full">
                <i class="fas fa-expand-alt"></i>
                View full context
            </div>
        `;

        // Make local sources clickable to show modal
        sourceItem.addEventListener('click', () => {
            showCitationModal(source);
        });
    }

    return sourceItem;
}

// Initialize citation modal event listeners
function initCitationModal() {
    const closeBtn = document.getElementById('citationModalClose');
    const overlay = document.getElementById('citationModalOverlay');

    if (closeBtn) {
        closeBtn.addEventListener('click', closeCitationModal);
    }

    if (overlay) {
        overlay.addEventListener('click', closeCitationModal);
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('citationModal');
            if (modal && modal.style.display === 'flex') {
                closeCitationModal();
            }
        }
    });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Extract filename from path
function extractFilename(path) {
    if (!path) return 'Unknown';
    return path.split('/').pop().split('\\').pop();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCitationModal);
} else {
    initCitationModal();
}
