document.addEventListener('DOMContentLoaded', () => {
    const incidentIdInput = document.getElementById('incidentIdInput');
    const fetchButton = document.getElementById('fetchTimelineButton');
    const timelineContainer = document.getElementById('timeline-container');
    let pollingInterval;

    fetchButton.addEventListener('click', () => {
        const incidentId = incidentIdInput.value.trim();
        if (incidentId) {
            // Clear previous timeline and stop old polling
            if (pollingInterval) clearInterval(pollingInterval);
            timelineContainer.innerHTML = '';

            // Fetch immediately and then poll every 5 seconds
            fetchAndRenderTimeline(incidentId);
            pollingInterval = setInterval(() => fetchAndRenderTimeline(incidentId), 5000);
        }
    });

    async function fetchAndRenderTimeline(incidentId) {
        try {
            const response = await fetch(`http://localhost:8004/timeline/${incidentId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const events = await response.json();
            renderTimeline(events);
        } catch (error) {
            console.error("Failed to fetch timeline:", error);
            timelineContainer.innerHTML = `<p class="error">Failed to load timeline. Is the orchestrator running?</p>`;
            if (pollingInterval) clearInterval(pollingInterval);
        }
    }

    function renderTimeline(events) {
        timelineContainer.innerHTML = ''; // Clear existing content
        events.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = `timeline-event ${event.type}`;

            const eventDate = new Date(event.event_ts).toLocaleString();
            let title = `Event: ${event.type}`;
            let contentHtml = `<pre>${JSON.stringify(event.payload, null, 2)}</pre>`;

            // Customize display for specific event types
            if (event.type === 'alert') {
                title = `🚨 Alert Firing: ${event.payload.labels.alertname}`;
                contentHtml = `<p>${event.payload.annotations.summary}</p><pre>${JSON.stringify(event.payload, null, 2)}</pre>`;
            } else if (event.type === 'ai_insight_docqa') {
                title = `🤖 AI Insight: Document QA`;
                contentHtml = `<p><strong>Suggestion:</strong> ${event.payload.answer}</p><p><strong>Source:</strong> <code>${event.payload.source}</code></p>`;
            }

            eventElement.innerHTML = `
                <div class="event-header">
                    <span class="event-title">${title}</span>
                    <span class="event-timestamp">${eventDate}</span>
                </div>
                <div class="event-body">
                    ${contentHtml}
                </div>
            `;
            timelineContainer.appendChild(eventElement);
        });
    }
});