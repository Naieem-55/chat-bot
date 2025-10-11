// Configuration
const API_BASE_URL = 'http://localhost:8002';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAnalytics();

    // Event listeners
    document.getElementById('refreshBtn').addEventListener('click', loadAnalytics);
    document.getElementById('exportBtn').addEventListener('click', exportFeedback);
});

// Load all analytics data
async function loadAnalytics() {
    await Promise.all([
        loadStats(),
        loadProblematicQueries(),
        loadHallucinations()
    ]);
}

// Load feedback statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback/stats`);
        const data = await response.json();

        // Update stat cards
        document.getElementById('totalFeedback').textContent = data.total_feedback || 0;
        document.getElementById('positiveFeedback').textContent = data.positive_count || 0;
        document.getElementById('negativeFeedback').textContent = data.negative_count || 0;
        document.getElementById('hallucinationCount').textContent = data.hallucination_count || 0;

        // Update percentages
        document.getElementById('positiveRate').textContent =
            `${((data.positive_rate || 0) * 100).toFixed(1)}%`;
        document.getElementById('negativeRate').textContent =
            `${(((1 - (data.positive_rate || 0)) * 100)).toFixed(1)}%`;
        document.getElementById('hallucinationRate').textContent =
            `${((data.hallucination_rate || 0) * 100).toFixed(1)}%`;

        // Update hallucination reasons
        if (data.common_hallucination_reasons) {
            displayHallucinationReasons(data.common_hallucination_reasons);
        }

    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load problematic queries
async function loadProblematicQueries() {
    const container = document.getElementById('problematicQueries');

    try {
        const response = await fetch(`${API_BASE_URL}/feedback/problematic-queries`);
        const data = await response.json();

        if (data.problematic_queries && data.problematic_queries.length > 0) {
            container.innerHTML = data.problematic_queries.map(item => `
                <div class="data-item">
                    <div class="data-item-header">
                        <div class="data-item-title">"${item.query}"</div>
                        <div class="data-item-badge badge-negative">
                            ${(item.negative_rate * 100).toFixed(0)}% negative
                        </div>
                    </div>
                    <div class="data-item-meta">
                        <span>Total feedback: ${item.total_feedback}</span>
                        <span>Negative: ${item.negative_count}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div>No problematic queries detected</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading problematic queries:', error);
        container.innerHTML = `<div class="empty-state">Error loading data</div>`;
    }
}

// Load hallucinations
async function loadHallucinations() {
    const container = document.getElementById('hallucinationsList');

    try {
        const response = await fetch(`${API_BASE_URL}/feedback/hallucinations`);
        const data = await response.json();

        if (data.hallucinations && data.hallucinations.length > 0) {
            container.innerHTML = data.hallucinations.map(item => `
                <div class="data-item">
                    <div class="data-item-header">
                        <div class="data-item-title">"${item.user_query}"</div>
                        <div class="data-item-badge badge-hallucination">
                            ${item.feedback === 'negative' ? '👎' : '👍'} ${item.feedback}
                        </div>
                    </div>
                    <div class="data-item-content">
                        ${item.bot_response}
                    </div>
                    <div class="data-item-meta">
                        <span>Reasons: ${item.reasons.join(', ')}</span>
                        <span>${new Date(item.timestamp).toLocaleString()}</span>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div>No hallucinations detected</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading hallucinations:', error);
        container.innerHTML = `<div class="empty-state">Error loading data</div>`;
    }
}

// Display hallucination reasons
function displayHallucinationReasons(reasons) {
    const container = document.getElementById('hallucinationReasons');

    if (Object.keys(reasons).length > 0) {
        container.innerHTML = Object.entries(reasons)
            .map(([reason, count]) => `
                <div class="reason-item">
                    <span class="reason-text">${formatReasonText(reason)}</span>
                    <span class="reason-count">${count}</span>
                </div>
            `).join('');
    } else {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <div>No hallucination patterns detected</div>
            </div>
        `;
    }
}

// Format reason text
function formatReasonText(reason) {
    // Convert snake_case to readable text
    return reason
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Export feedback
async function exportFeedback() {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback/export`);
        const data = await response.json();

        if (data.export_path) {
            alert(`Feedback exported successfully to:\n${data.export_path}`);
        }
    } catch (error) {
        console.error('Error exporting feedback:', error);
        alert('Failed to export feedback');
    }
}
