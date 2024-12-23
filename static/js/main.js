// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const downloadForm = document.getElementById('downloadForm');
    const downloadsContainer = document.getElementById('downloads');
    const activeDownloads = new Map();

    downloadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(downloadForm);
        const downloadItem = createDownloadItem(formData.get('url'));
        downloadsContainer.insertBefore(downloadItem, downloadsContainer.firstChild);

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                updateDownloadStatus(downloadItem, 'error', data.error);
                return;
            }
            
            const downloadId = data.download_id;
            activeDownloads.set(downloadId, downloadItem);
            startProgressPolling(downloadId);
        })
        .catch(error => {
            updateDownloadStatus(downloadItem, 'error', 'Failed to start download');
        });

        downloadForm.reset();
    });

    function createDownloadItem(url) {
        const item = document.createElement('div');
        item.className = 'download-item';
        item.innerHTML = `
            <div class="download-url">${url}</div>
            <div class="progress-bar">
                <div class="progress-bar-fill"></div>
            </div>
            <div class="download-status">
                <span class="status-text">Initializing...</span>
                <span class="progress-text">0%</span>
            </div>
            <div class="download-actions" style="display: none;">
                <button class="download-file-btn">Download File</button>
            </div>
        `;
        return item;
    }

    function updateDownloadStatus(downloadItem, type, message, progress = 0, downloadId = null) {
        const statusText = downloadItem.querySelector('.status-text');
        const progressText = downloadItem.querySelector('.progress-text');
        const progressBar = downloadItem.querySelector('.progress-bar-fill');
        const downloadActions = downloadItem.querySelector('.download-actions');
        const downloadButton = downloadItem.querySelector('.download-file-btn');

        if (type === 'error') {
            statusText.className = 'status-text error';
            statusText.textContent = message;
            progressText.style.display = 'none';
            downloadActions.style.display = 'none';
        } else if (type === 'completed') {
            statusText.className = 'status-text completed';
            statusText.textContent = message;
            progressText.textContent = '100%';
            progressBar.style.width = '100%';
            downloadActions.style.display = 'block';
            
            // Add click event for download button
            if (downloadId) {
                downloadButton.onclick = () => {
                    window.location.href = `/download/${downloadId}`;
                };
            }
        } else {
            statusText.textContent = message;
            progressText.textContent = `${Math.round(progress)}%`;
            progressBar.style.width = `${progress}%`;
        }
    }

    function startProgressPolling(downloadId) {
        const pollInterval = setInterval(() => {
            if (!activeDownloads.has(downloadId)) {
                clearInterval(pollInterval);
                return;
            }

            fetch(`/progress/${downloadId}`)
                .then(response => response.json())
                .then(data => {
                    const downloadItem = activeDownloads.get(downloadId);
                    
                    if (data.error) {
                        updateDownloadStatus(downloadItem, 'error', data.error);
                        activeDownloads.delete(downloadId);
                        clearInterval(pollInterval);
                        return;
                    }

                    if (data.completed) {
                        updateDownloadStatus(downloadItem, 'completed', data.status, 100, downloadId);
                        activeDownloads.delete(downloadId);
                        clearInterval(pollInterval);
                        return;
                    }

                    updateDownloadStatus(downloadItem, 'progress', data.status, data.progress);
                })
                .catch(error => {
                    const downloadItem = activeDownloads.get(downloadId);
                    updateDownloadStatus(downloadItem, 'error', 'Failed to fetch progress');
                    activeDownloads.delete(downloadId);
                    clearInterval(pollInterval);
                });
        }, 1000);
    }
});