/**
 * Function Executor Module
 * Handles function execution, file uploads, and result processing
 */

// Make key functions globally available
window.executeSelectedFunction = executeSelectedFunction;
window.handleFileSelect = handleFileSelect;
window.saveFunctionExecution = saveFunctionExecution;

/**
 * Execute the selected function with provided inputs
 * @param {Object} data - Function data
 * @param {HTMLElement} container - Container element
 */
function executeSelectedFunction(data, container) {
    // Clear previous execution results
    const existingResults = container.querySelectorAll('.execution-result');
    existingResults.forEach(result => result.remove());

    const inputs = container.querySelectorAll('input:not([type="file"]), textarea');
    const args = {};

    // Collect input values
    inputs.forEach(input => {
        args[input.name] = input.value;
    });

    const fileInput = container.querySelector('input[type="file"]');
    if (fileInput && fileInput.files.length > 0) {
        // Handle file upload execution
        uploadFiles(data.id, fileInput.files, args, container);
    } else {
        // Handle regular execution
        executeFunction(data.id, args, container);
    }
}

/**
 * Handle file selection and preview
 * @param {Event} event - File input change event
 */
function handleFileSelect(event) {
    const files = event.target.files;
    const preview = document.getElementById('filePreview');
    preview.innerHTML = '';

    if (files.length > 0) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const previewItem = document.createElement('div');
            previewItem.className = 'file-preview-item';
            previewItem.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <small>${(file.size / 1024).toFixed(1)} KB</small>
            `;
            preview.appendChild(previewItem);
        }
    }
}

/**
 * Execute function via API
 * @param {string} funcId - Function ID
 * @param {Object} args - Function arguments
 * @param {HTMLElement} container - Container element
 */
function executeFunction(funcId, args, container) {
    fetch(`/api/function/${selectedFunctionId}/execute`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ arguments: args })
    })
    .then(response => response.json())
    .then(data => {
        handleExecutionResult(container, data.success ? data.result : data, data.success);
    })
    .catch(error => {
        handleExecutionResult(container, { error: error.message }, false);
    });
}

/**
 * Upload files and execute function
 * @param {string} funcId - Function ID
 * @param {FileList} files - Selected files
 * @param {Object} args - Function arguments
 * @param {HTMLElement} container - Container element
 */
function uploadFiles(funcId, files, args, container) {
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files', file));
    formData.append('arguments', JSON.stringify(args));

    fetch(`/api/function/${selectedFunctionId}/execute`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        handleExecutionResult(container, data.success ? data.result : data, data.success);
    })
    .catch(error => {
        handleExecutionResult(container, { error: error.message }, false);
    });
}

/**
 * Handle execution result display
 * @param {HTMLElement} container - Container element
 * @param {*} result - Execution result
 * @param {boolean} isSuccess - Success flag
 */
function handleExecutionResult(container, result, isSuccess) {
    // Remove progress indicator if exists
    const progressDiv = container.querySelector('.execution-progress');
    if (progressDiv) progressDiv.remove();

    // Create result display
    const resultDiv = document.createElement('div');
    resultDiv.className = 'execution-result';
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = isSuccess ?
        `<h4>Результат выполнения:</h4><div>${formatResult(result)}</div>` :
        `<h4 style="color: #ff4444;">Ошибка выполнения:</h4><div>${result.error || result}</div>`;

    container.appendChild(resultDiv);

    // Update execute button
    const executeBtn = container.querySelector('.execute-btn');
    executeBtn.style.display = 'flex';
    executeBtn.innerHTML = '<i class="fas fa-redo"></i> Выполнить снова';
}

/**
 * Format execution result for display
 * @param {*} result - Raw result data
 * @returns {string} Formatted HTML
 */
function formatResult(result) {
    if (typeof result === 'string') {
        try {
            result = JSON.parse(result);
        } catch (e) {
            return result;
        }
    }

    if (typeof result !== 'object') return String(result);

    // Special handling for YOLO detection results
    if (result.detected_objects) {
        return formatYoloResult(result);
    }

    // Generic object formatting
    let html = '<div class="result-content">';
    for (const [key, value] of Object.entries(result)) {
        html += `<p><strong>${key}:</strong> ${JSON.stringify(value)}</p>`;
    }
    html += '</div>';

    return html;
}

/**
 * Format YOLO detection results
 * @param {Object} result - YOLO result object
 * @returns {string} Formatted HTML
 */
function formatYoloResult(result) {
    let html = `<div class="yolo-detection">
        <h5>Обнаруженные объекты (${result.detected_objects.length}):</h5>`;

    result.detected_objects.forEach(obj => {
        html += `<div class="yolo-object">
            <span>${obj.class}</span>
            <span>${(obj.confidence * 100).toFixed(1)}%</span>
        </div>`;
    });

    // Add image preview if available
    if (result.output_image) {
        const imageUrl = `/uploads/${result.output_image.replace(/\\/g, '/')}`;
        html += `<div class="image-preview">
            <img src="${imageUrl}" alt="Результат обнаружения"
                style="max-width: 100%; margin-top: 1rem; cursor: pointer;"
                onclick="expandImage(this)">
        </div>`;
    }

    return html;
}

/**
 * Expand image in modal
 * @param {HTMLImageElement} imgElement - Image element to expand
 */
function expandImage(imgElement) {
    let modal = document.getElementById('imageModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'imageModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <span class="close">&times;</span>
            <img class="modal-content-img" id="expandedImage">
        `;
        document.body.appendChild(modal);

        // Add modal styles
        const style = document.createElement('style');
        style.textContent = `
            .modal {
                display: none;
                position: fixed;
                z-index: 1001;
                padding-top: 60px;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
            }
            .modal-content-img {
                margin: auto;
                display: block;
                max-width: 90%;
                max-height: 80vh;
                border: var(--cyber-border);
                box-shadow: 0 0 10px 2px #8f8f8f;
                border-radius: var(--border-radius);
            }
            .close {
                position: absolute;
                top: 15px;
                right: 35px;
                color: #fababa;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: #bbb;
            }
        `;
        document.head.appendChild(style);
    }

    const modalImg = document.getElementById('expandedImage');
    modal.style.display = 'block';
    modalImg.src = imgElement.src;

    // Close modal handlers
    document.querySelector('.close').onclick = function() {
        modal.style.display = 'none';
    }

    modal.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    }

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });
}

/**
 * Save function execution record
 * @param {string} funcId - Function ID
 * @param {Object} args - Arguments
 * @param {*} result - Result
 * @param {boolean} isSuccess - Success flag
 */
function saveFunctionExecution(funcId, args, result, isSuccess) {
    fetch('/api/function/execution', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            function_id: funcId,
            arguments: args,
            result: typeof result === 'object' ? JSON.stringify(result) : result,
            success: isSuccess
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Execution saved:', data);
    })
    .catch(error => {
        console.error('Error saving execution:', error);
    });
}