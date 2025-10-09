/**
 * Function Selector Module
 * Handles function selection, interface rendering, and user interactions
 */

let selectedFunctionId = null;
let selectedFunctionInfo = null;

// Make functions globally available for HTML inline event handlers
window.selectFunction = selectFunction;

/**
 * Handle function selection from dropdown
 * @param {HTMLSelectElement} select - The select element
 */
function selectFunction(select) {
    const functionId = select.value;
    const container = document.getElementById('functionContainer');

    // Reset selection state
    selectedFunctionId = null;
    selectedFunctionInfo = null;

    if (!functionId) {
        container.innerHTML = '<p class="empty-state">Выберите модуль из списка</p>';
        container.classList.remove('loading');
        return;
    }

    // Show loading state
    container.classList.add('loading');
    container.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Загрузка модуля...</p>
        </div>
    `;

    // Fetch function interaction data
    fetch(`/api/function/${functionId}/interaction`)
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error(getErrorMessage(response.status));
        })
        .then(data => {
            container.classList.remove('loading');
            if (data.success) {
                selectedFunctionId = functionId;
                selectedFunctionInfo = {
                    id: functionId,
                    name: data.name,
                    interaction: data.interaction
                };
                renderFunctionInterface(data, container);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка модуля');
            }
        })
        .catch(error => {
            container.classList.remove('loading');
            showErrorState(container, error.message);
        });
}

/**
 * Render the function interface based on interaction data
 * @param {Object} data - Function interaction data
 * @param {HTMLElement} container - Container element
 */
function renderFunctionInterface(data, container) {
    let html = '';

    if (data && data.name && data.interaction && data.interaction.usage) {
        html = `
            <div class="function-header">
                <h3><i class="fab fa-python"></i> ${data.name}</h3>
                <p class="function-description">${data.interaction.description}</p>
            </div>
            <div class="function-inputs">
                ${generateInputFields(data.interaction.usage)}
        `;

        // Add file upload section if supported
        if (data.interaction.file_upload?.allowed) {
            html += `
                <div class="input-group file-upload-group">
                    <label>Загрузить файл: <small>${data.interaction.file_upload.types.join(', ')}</small></label>
                    <div class="file-upload-wrapper">
                        <label class="cyber-upload-btn">
                            <i class="fas fa-cloud-upload-alt"></i> Выберите файл
                            <input type="file" id="functionFileInput"
                                accept="${data.interaction.file_upload.types.join(',')}"
                                ${data.interaction.file_upload.multiple ? 'multiple' : ''}
                                style="display: none;">
                        </label>
                        <div id="filePreview"></div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
    } else {
        console.error("Некорректные данные функции:", data);
        container.innerHTML = "<p class='error-message'>Ошибка: Некорректные данные функции</p>";
        return;
    }

    // Create execute button
    const executeBtn = document.createElement('button');
    executeBtn.className = 'execute-btn';
    executeBtn.innerHTML = '<i class="fas fa-play"></i> Выполнить';
    executeBtn.onclick = () => executeSelectedFunction(data, container);

    // Update container
    container.innerHTML = html;
    container.appendChild(executeBtn);

    // Setup file input handler
    const fileInput = document.getElementById('functionFileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

/**
 * Generate input fields based on function usage specification
 * @param {Object} usage - Usage specification object
 * @returns {string} HTML string for input fields
 */
function generateInputFields(usage) {
    let html = '';
    for (const [param, desc] of Object.entries(usage)) {
        html += `
            <div class="input-group">
                <label>${desc}</label>
                <input type="text" name="${param}" placeholder="Введите ${param}" class="cyber-input">
            </div>
        `;
    }
    return html;
}

/**
 * Show error state in container
 * @param {HTMLElement} container - Container element
 * @param {string} message - Error message
 */
function showErrorState(container, message) {
    let icon = 'fa-exclamation-triangle';
    let errorClass = 'error-message';

    if (message.includes('позже')) {
        icon = 'fa-clock';
        errorClass = 'error-message-warning';
    } else if (message.includes('не найден')) {
        icon = 'fa-search';
        errorClass = 'error-message-not-found';
    } else if (message.includes('Доступ')) {
        icon = 'fa-lock';
        errorClass = 'error-message-access';
    }

    container.innerHTML = `
        <div class="${errorClass}">
            <i class="fas ${icon}"></i>
            <p>${message}</p>
            ${message.includes('позже') ?
                '<button class="retry-btn" onclick="selectFunction(document.getElementById(\'functionSelect\'))">Попробовать снова</button>' :
                ''}
        </div>
    `;
}

/**
 * Get appropriate error message based on HTTP status
 * @param {number} status - HTTP status code
 * @returns {string} Error message
 */
function getErrorMessage(status) {
    switch (status) {
        case 404:
            return 'Модуль не найден';
        case 429:
            return 'Слишком много запросов. Попробуйте позже';
        case 403:
            return 'Модуль сейчас не доступен';
        default:
            return `Ошибка сервера (${status})`;
    }
}