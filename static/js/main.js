"use strict";

/* =========================================================
   E.A.D.A
   Explainable Adaptive Decision Agent

   Main Frontend Controller
   ========================================================= */


/* =========================================================
   API Endpoints
   ========================================================= */

const API = {
    decision: "/decision",
    train: "/train",
    analytics: "/analytics",

    /*
     * The first URL should be used by your backend for JSON history.
     * The remaining URLs are automatic fallbacks.
     */
    history: [
        "/history?format=json",
        "/api/history",
        "/history/data"
    ]
};


/* =========================================================
   Application State
   ========================================================= */

const appState = {
    charts: {},
    history: [],
    filteredHistory: [],
    lastDecision: null
};


/* =========================================================
   Application Start
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initializeRangeInputs();
    initializeDecisionForm();
    initializeTraining();
    initializeAnalytics();
    initializeHistoryPage();
    initializeRefreshButtons();
    initializeClearButton();

    loadDashboardData();
});


/* =========================================================
   DOM Helpers
   ========================================================= */

function getElement(...ids) {
    for (const id of ids) {
        const element = document.getElementById(id);

        if (element) {
            return element;
        }
    }

    return null;
}


function getElementValue(...ids) {
    const element = getElement(...ids);

    if (!element) {
        return "";
    }

    return element.value?.trim() ?? "";
}


function setText(value, ...ids) {
    const element = getElement(...ids);

    if (element) {
        element.textContent = value;
    }
}


function setHTML(value, ...ids) {
    const element = getElement(...ids);

    if (element) {
        element.innerHTML = value;
    }
}


function showElement(...ids) {
    const element = getElement(...ids);

    if (element) {
        element.classList.remove("hidden");
    }
}


function hideElement(...ids) {
    const element = getElement(...ids);

    if (element) {
        element.classList.add("hidden");
    }
}


/* =========================================================
   General Utilities
   ========================================================= */

function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function toNumber(value, fallback = 0) {
    const number = Number(value);

    return Number.isFinite(number) ? number : fallback;
}


function formatNumber(value, decimals = 2) {
    return toNumber(value).toFixed(decimals);
}


function formatPercentage(value) {
    let number = toNumber(value);

    /*
     * Backend may return confidence as 0.87 or 87.
     */
    if (number >= 0 && number <= 1) {
        number *= 100;
    }

    return `${number.toFixed(1)}%`;
}


function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString();
}


function normalizeAction(action) {
    const value = String(action ?? "Unknown")
        .replaceAll("_", " ")
        .trim();

    return value.replace(/\b\w/g, character => character.toUpperCase());
}


function normalizeRisk(risk) {
    const value = String(risk ?? "Unknown").toLowerCase();

    if (value.includes("low")) {
        return "Low";
    }

    if (value.includes("medium") || value.includes("moderate")) {
        return "Medium";
    }

    if (value.includes("high")) {
        return "High";
    }

    return normalizeAction(risk);
}


/* =========================================================
   Message Display
   ========================================================= */

function showMessage(message, type = "info") {
    const messageBox = getElement(
        "systemMessage",
        "messageBox",
        "statusMessage"
    );

    if (!messageBox) {
        console.log(`[${type.toUpperCase()}] ${message}`);
        return;
    }

    messageBox.textContent = message;

    messageBox.className =
        `system-message ${type}-message fade-in`;

    messageBox.classList.remove("hidden");

    window.clearTimeout(showMessage.timeout);

    showMessage.timeout = window.setTimeout(() => {
        messageBox.classList.add("hidden");
    }, 5000);
}


/* =========================================================
   Button Loading State
   ========================================================= */

function setButtonLoading(button, loading, loadingText = "Loading...") {
    if (!button) {
        return;
    }

    if (loading) {
        button.dataset.originalText = button.textContent;
        button.textContent = loadingText;
        button.disabled = true;
        button.classList.add("button-loading");
    } else {
        button.textContent =
            button.dataset.originalText || button.textContent;

        button.disabled = false;
        button.classList.remove("button-loading");
    }
}


/* =========================================================
   API Request Helper
   ========================================================= */

async function requestJSON(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    const contentType =
        response.headers.get("content-type") || "";

    let data;

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        const text = await response.text();

        throw new Error(
            text.startsWith("<!DOCTYPE") || text.startsWith("<html")
                ? `Expected JSON from ${url}, but received an HTML page.`
                : text || `Request failed with status ${response.status}.`
        );
    }

    if (!response.ok) {
        throw new Error(
            data.message ||
            data.error ||
            `Request failed with status ${response.status}.`
        );
    }

    return data;
}


async function requestFirstAvailable(urls, options = {}) {
    let lastError;

    for (const url of urls) {
        try {
            return await requestJSON(url, options);
        } catch (error) {
            lastError = error;
            console.warn(`Request failed for ${url}:`, error.message);
        }
    }

    throw lastError || new Error("No API endpoint was available.");
}


/* =========================================================
   Range Inputs
   ========================================================= */

function initializeRangeInputs() {
    const rangeConfigurations = [
        {
            inputIds: ["priority", "priorityInput"],
            outputIds: ["priorityValue"]
        },
        {
            inputIds: ["complexity", "complexityInput"],
            outputIds: ["complexityValue"]
        },
        {
            inputIds: ["resource", "resources", "resourcesInput"],
            outputIds: ["resourcesValue"]
        },
        {
            inputIds: ["deadline", "deadlineInput"],
            outputIds: ["deadlineValue"]
        }
    ];

    rangeConfigurations.forEach(configuration => {
        const input = getElement(...configuration.inputIds);
        const output = getElement(...configuration.outputIds);

        if (!input || !output || input.type !== "range") {
            return;
        }

        const updateOutput = () => {
            output.textContent = input.value;
        };

        updateOutput();
        input.addEventListener("input", updateOutput);
    });
}


/* =========================================================
   Decision Form
   ========================================================= */

function initializeDecisionForm() {
    const form = getElement(
        "taskForm",
        "decisionForm",
        "analyzeForm"
    );

    if (!form) {
        return;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        await submitDecision();
    });
}


async function submitDecision() {

    const button = getElement(
        "analyzeBtn",
        "decisionBtn",
        "submitTaskBtn"
    );

    const payload = collectDecisionPayload();

    const validationError = validateDecisionPayload(payload);

    if (validationError) {
        showMessage(validationError, "error");
        return;
    }

    setButtonLoading(
        button,
        true,
        "Analyzing..."
    );

    try {

        const response = await requestJSON(
            API.decision,
            {
                method: "POST",
                body: JSON.stringify(payload)
            }
        );

        const decision =
            response.decision ??
            response.result ??
            response.data ??
            response;

        appState.lastDecision = decision;

        displayDecision(decision);

        showMessage(
            "Decision generated successfully.",
            "success"
        );

        await Promise.allSettled([
            loadAnalytics(),
            loadHistory()
        ]);

    } catch (error) {

        console.error(
            "Decision request failed:",
            error
        );

        showMessage(
            error.message,
            "error"
        );

    } finally {

        setButtonLoading(
            button,
            false
        );

    }
}


function collectDecisionPayload() {
    return {
        task: getElementValue(
            "task",
            "taskInput",
            "taskDescription"
        ),

        priority: toNumber(
            getElementValue(
                "priority",
                "priorityInput"
            )
        ),

        deadline: toNumber(
            getElementValue(
                "deadline",
                "deadlineInput"
            )
        ),

        complexity: getElementValue(
            "complexity",
            "complexityInput"
        ),

        resource: (
            document.getElementById("resource") ||
            document.getElementById("resources") ||
            document.getElementById("resourceInput") ||
            document.getElementById("resourcesInput") ||
            document.getElementById("resourceAvailability") ||
            document.querySelector('[name="resource"]') ||
            document.querySelector('[name="resources"]')
        )?.value?.trim() || "",

        success: toNumber(
            getElementValue(
                "success",
                "successInput"
            )
        ),

        failure: toNumber(
            getElementValue(
                "failure",
                "failureInput"
            )
        )
    };
}


function validateDecisionPayload(payload) {
    if (!payload.task) {
        return "Please enter a task description.";
    }

    if (payload.task.length < 3) {
        return "Task description must contain at least 3 characters.";
    }

    if (!payload.complexity) {
        return "Please select task complexity.";
    }

    if (!payload.resource) {
        return "Please select resource availability.";
    }

    const numericFields = [
        ["Priority", payload.priority],
        ["Deadline", payload.deadline],
        ["Success", payload.success],
        ["Failure", payload.failure]
    ];

    for (const [label, value] of numericFields) {
        if (!Number.isFinite(value)) {
            return `${label} must be a valid number.`;
        }
    }

    if (payload.success < 0 || payload.failure < 0) {
        return "Success and failure values cannot be negative.";
    }

    return null;
}


/* =========================================================
   Display Decision
   ========================================================= */

function displayDecision(data) {
    const action =
        data.action ??
        data.decision ??
        data.recommended_action ??
        data.recommendation ??
        "Unknown";

    const confidence =
        data.confidence ??
        data.confidence_score ??
        0;

    const risk =
        data.risk ??
        data.risk_level ??
        "Unknown";

    const reward =
        data.reward ??
        data.expected_reward ??
        data.reward_score ??
        0;

    const explanation =
        data.explanation ??
        data.reason ??
        data.reasoning ??
        "No explanation was returned.";

    setText(
        normalizeAction(action),
        "action",
        "decisionAction",
        "actionValue",
        "recommendedAction"
    );

    setText(
        formatPercentage(confidence),
        "confidence",
        "confidenceValue",
        "decisionConfidence"
    );

    setText(
        `Confidence: ${formatPercentage(confidence)}`,
        "confidenceText"
    );

    setText(
        normalizeRisk(risk),
        "risk",
        "riskValue",
        "decisionRisk"
    );

    setText(
        formatNumber(reward),
        "reward",
        "rewardValue",
        "decisionReward"
    );

    setText(
        explanation,
        "explanation",
        "explanationText",
        "decisionExplanation"
    );

    updateActionClass(action);
    updateRiskClass(risk);
    displayQValues(data.q_values ?? data.qValues ?? {});
    showElement(
        "decisionResult",
        "decisionOutput",
        "decisionPanel",
        "resultSection",
        "resultSection"
    );

    const resultPanel = getElement(
        "decisionResult",
        "decisionOutput",
        "decisionPanel",
        "resultSection"
    );

    resultPanel?.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}


function updateActionClass(action) {
    const element = getElement(
        "action",
        "decisionAction",
        "actionValue",
        "recommendedAction"
    );

    if (!element) {
        return;
    }

    element.classList.remove(
        "action-execute",
        "action-allocate",
        "action-split",
        "action-delay"
    );

    const value = String(action).toLowerCase();

    if (value.includes("execute")) {
        element.classList.add("action-execute");
    } else if (value.includes("allocate")) {
        element.classList.add("action-allocate");
    } else if (value.includes("split")) {
        element.classList.add("action-split");
    } else if (value.includes("delay")) {
        element.classList.add("action-delay");
    }
}


function updateRiskClass(risk) {
    const element = getElement(
        "risk",
        "riskValue",
        "decisionRisk"
    );

    if (!element) {
        return;
    }

    element.classList.remove(
        "risk-low",
        "risk-medium",
        "risk-high"
    );

    const value = String(risk).toLowerCase();

    if (value.includes("low")) {
        element.classList.add("risk-low");
    } else if (
        value.includes("medium") ||
        value.includes("moderate")
    ) {
        element.classList.add("risk-medium");
    } else if (value.includes("high")) {
        element.classList.add("risk-high");
    }
}


function displayQValues(qValues) {
    const container = getElement(
        "qValues",
        "qValuesContainer",
        "qValueGrid"
    );

    if (!container) {
        return;
    }

    const entries = Array.isArray(qValues)
        ? qValues.map((value, index) => [
            `Action ${index + 1}`,
            value
        ])
        : Object.entries(qValues || {});

    if (entries.length === 0) {
        container.innerHTML =
            '<p class="text-muted">No Q-values available.</p>';

        return;
    }

    const bestValue = Math.max(
        ...entries.map(([, value]) => toNumber(value))
    );

    container.innerHTML = entries
        .map(([action, value]) => {
            const numericValue = toNumber(value);
            const bestClass =
                numericValue === bestValue ? "best-action" : "";

            return `
                <div class="q-value-card ${bestClass}">
                    <span>${escapeHTML(normalizeAction(action))}</span>
                    <strong>${formatNumber(numericValue, 4)}</strong>
                </div>
            `;
        })
        .join("");
}


/* =========================================================
   Clear Form
   ========================================================= */

function initializeClearButton() {
    const button = getElement(
        "clearBtn",
        "resetBtn",
        "clearFormBtn"
    );

    if (!button) {
        return;
    }

    button.addEventListener("click", () => {
        const form = getElement(
            "taskForm",
            "decisionForm",
            "analyzeForm"
        );

        form?.reset();

        initializeRangeInputs();

        hideElement(
            "decisionResult",
            "decisionOutput",
            "decisionPanel"
        );

        showMessage("Form cleared.", "info");
    });
}


/* =========================================================
   Training
   ========================================================= */

function initializeTraining() {
    const button = getElement(
        "trainBtn",
        "trainAgentBtn"
    );

    if (!button) {
        return;
    }

    button.addEventListener("click", trainAgent);
}


async function trainAgent() {
    const button = getElement(
        "trainBtn",
        "trainAgentBtn"
    );

    setButtonLoading(button, true, "Training...");

    try {
        const response = await requestJSON(API.train, {
            method: "POST",
            body: JSON.stringify({})
        });

        const result =
            response.result ??
            response.training ??
            response.data ??
            response;

        displayTrainingResult(result);
        showMessage("Agent training completed successfully.", "success");

        await loadAnalytics();
    } catch (error) {
        console.error("Training failed:", error);
        showMessage(error.message, "error");
    } finally {
        setButtonLoading(button, false);
    }
}


function displayTrainingResult(result) {

    // Top dashboard cards
    setText(
        result.episodes ??
        result.total_episodes ??
        0,
        "iterations"
    );

    setText(
        formatNumber(
            result.average_reward ??
            result.final_reward ??
            result.reward ??
            0,
            2
        ),
        "reward"
    );


    // Training details
    setText(
        result.dataset_size ?? 0,
        "datasetSize",
        "trainingDatasetSize"
    );

    setText(
        result.q_states ??
        result.q_table_states ??
        0,
        "qTableStates",
        "qStates"
    );

    setText(
        formatPercentage(
            result.success_rate ??
            result.final_success_rate ??
            0
        ),
        "trainingSuccessRate",
        "successRate"
    );

    setText(
        formatNumber(
            result.learning_progress ?? 0,
            2
        ),
        "learningProgress"
    );


    // Optional epsilon
    setText(
        formatNumber(
            result.epsilon ??
            result.final_epsilon ??
            0,
            4
        ),
        "trainingEpsilon",
        "epsilonValue"
    );


    // Show results
    showElement(
        "trainingResult",
        "trainingMetrics"
    );
}


/* =========================================================
   Analytics
   ========================================================= */

function initializeAnalytics() {
    const button = getElement(
        "refreshAnalyticsBtn",
        "analyticsRefreshBtn"
    );

    button?.addEventListener("click", loadAnalytics);
}


async function loadAnalytics() {
    const analyticsSection = getElement(
        "analyticsSection",
        "analytics"
    );

    if (!analyticsSection) {
        return;
    }

    try {
        const response = await requestJSON(API.analytics);

        const data =
            response.analytics ??
            response.data ??
            response;

        updateStatistics(data.statistics ?? data.stats ?? data);
        updateAnalyticsCharts(data);
    } catch (error) {
        console.error("Analytics loading failed:", error);
    }
}


function updateStatistics(statistics) {
    setText(
        statistics.total_decisions ??
        statistics.total ??
        0,
        "totalDecisions",
        "totalTasks"
    );

    setText(
        formatPercentage(
            statistics.average_confidence ??
            statistics.avg_confidence ??
            0
        ),
        "averageConfidence",
        "avgConfidence"
    );

    setText(
        formatNumber(
            statistics.average_reward ??
            statistics.avg_reward ??
            0
        ),
        "averageReward",
        "avgReward"
    );

    setText(
        statistics.high_risk_count ??
        statistics.high_risk ??
        0,
        "highRiskCount",
        "highRiskTasks"
    );
}


function updateAnalyticsCharts(data) {
    if (typeof Chart === "undefined") {
        console.warn(
            "Chart.js is not loaded. Analytics charts were skipped."
        );

        return;
    }

    createOrUpdateChart(
        "rewardChart",
        "line",
        data.reward_history ??
        data.rewards ??
        [],
        "Reward"
    );

    createOrUpdateChart(
        "successChart",
        "line",
        data.success_history ??
        data.success_rates ??
        [],
        "Success Rate"
    );

    createDistributionChart(
        "actionChart",
        data.action_distribution ??
        data.actions ??
        {}
    );

    createDistributionChart(
        "confidenceChart",
        data.confidence_distribution ??
        data.confidence_histogram ??
        {}
    );
}


function createOrUpdateChart(canvasId, type, values, label) {
    const canvas = getElement(canvasId);

    if (!canvas || !Array.isArray(values)) {
        return;
    }

    const labels = values.map((_, index) => index + 1);

    replaceChart(canvasId, {
        type,
        data: {
            labels,
            datasets: [
                {
                    label,
                    data: values,
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false
                }
            ]
        },
        options: getChartOptions()
    });
}


function createDistributionChart(canvasId, distribution) {
    const canvas = getElement(canvasId);

    if (!canvas || !distribution) {
        return;
    }

    const entries = Array.isArray(distribution)
        ? distribution.map((value, index) => [
            `Group ${index + 1}`,
            value
        ])
        : Object.entries(distribution);

    replaceChart(canvasId, {
        type: "bar",
        data: {
            labels: entries.map(([label]) => normalizeAction(label)),
            datasets: [
                {
                    label: "Count",
                    data: entries.map(([, value]) => toNumber(value)),
                    borderWidth: 1
                }
            ]
        },
        options: getChartOptions()
    });
}


function replaceChart(canvasId, configuration) {
    if (appState.charts[canvasId]) {
        appState.charts[canvasId].destroy();
    }

    const canvas = getElement(canvasId);

    appState.charts[canvasId] =
        new Chart(canvas.getContext("2d"), configuration);
}


function getChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,

        plugins: {
            legend: {
                labels: {
                    color: "#d4daec"
                }
            }
        },

        scales: {
            x: {
                ticks: {
                    color: "#9ca7c4"
                },

                grid: {
                    color: "rgba(255,255,255,.05)"
                }
            },

            y: {
                beginAtZero: true,

                ticks: {
                    color: "#9ca7c4"
                },

                grid: {
                    color: "rgba(255,255,255,.05)"
                }
            }
        }
    };
}


/* =========================================================
   History
   ========================================================= */

function initializeHistoryPage() {
    const searchInput = getElement(
        "historySearch",
        "searchHistory",
        "searchInput"
    );

    const filter = getElement(
        "historyFilter",
        "actionFilter",
        "riskFilter"
    );

    const exportButton = getElement(
        "exportHistoryBtn",
        "exportBtn"
    );

    searchInput?.addEventListener("input", filterHistory);
    filter?.addEventListener("change", filterHistory);
    exportButton?.addEventListener("click", exportHistoryCSV);
}


/* =========================================================
   History
   ========================================================= */

async function loadHistory() {

    const historyBody = getElement(
        "historyTableBody",
        "recentHistoryBody",
        "historyBody"
    );

    if (!historyBody) {
        return;
    }

    try {

        const response = await requestJSON(
            "/history?format=json"
        );

        const records =
            Array.isArray(response.history)
                ? response.history
                : [];

        appState.history = records;

        appState.filteredHistory = [
            ...records
        ];

        renderHistory(
            appState.filteredHistory
        );

        updateHistoryStatistics(
            records
        );

    } catch (error) {

        console.error(
            "History loading failed:",
            error
        );

        historyBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    Unable to load history.
                </td>
            </tr>
        `;
    }
}


function filterHistory() {

    const searchValue = getElementValue(
        "historySearch",
        "searchHistory",
        "searchInput"
    ).toLowerCase();

    const filterValue = getElementValue(
        "historyFilter",
        "actionFilter",
        "riskFilter"
    ).toLowerCase();


    appState.filteredHistory =
        appState.history.filter(
            record => {

                const task = String(
                    record.task ?? ""
                ).toLowerCase();

                const action = String(
                    record.action ?? ""
                ).toLowerCase();

                const risk = String(
                    record.risk ?? ""
                ).toLowerCase();


                const matchesSearch =
                    !searchValue ||
                    task.includes(
                        searchValue
                    ) ||
                    action.includes(
                        searchValue
                    ) ||
                    risk.includes(
                        searchValue
                    );


                const matchesFilter =
                    !filterValue ||
                    filterValue === "all" ||
                    risk === filterValue ||
                    action.includes(
                        filterValue
                    );


                return (
                    matchesSearch &&
                    matchesFilter
                );
            }
        );


    renderHistory(
        appState.filteredHistory
    );
}


function renderHistory(records) {

    const body = getElement(
        "historyTableBody",
        "recentHistoryBody",
        "historyBody"
    );

    if (!body) {
        return;
    }


    if (!Array.isArray(records) ||
        records.length === 0) {

        body.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    No decision history available.
                </td>
            </tr>
        `;

        return;
    }


    body.innerHTML = records
        .map(record => {

            const task =
                record.task ??
                "—";

            const action =
                record.action ??
                record.decision ??
                "—";

            const reward =
                record.reward ??
                0;

            const confidence =
                record.confidence ??
                0;

            const risk =
                normalizeRisk(
                    record.risk ??
                    "Unknown"
                );

            const date =
                record.created_at ??
                record.timestamp ??
                record.date ??
                "—";

            const riskClass =
                risk.toLowerCase();


            return `
                <tr>

                    <td>
                        ${escapeHTML(task)}
                    </td>

                    <td>
                        ${escapeHTML(
                            normalizeAction(action)
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            formatNumber(
                                reward,
                                2
                            )
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            formatPercentage(
                                confidence
                            )
                        )}
                    </td>

                    <td>
                        <span
                            class="status-badge ${escapeHTML(riskClass)}"
                        >
                            ${escapeHTML(risk)}
                        </span>
                    </td>

                    <td>
                        ${escapeHTML(
                            formatDate(date)
                        )}
                    </td>

                </tr>
            `;
        })
        .join("");
}


/* =========================================================
   History Statistics
   ========================================================= */

function updateHistoryStatistics(records) {

    if (!Array.isArray(records)) {
        return;
    }


    const totalDecisions =
        records.length;


    let totalReward = 0;

    let totalConfidence = 0;

    let highRiskCount = 0;


    records.forEach(record => {

        totalReward += toNumber(
            record.reward,
            0
        );

        totalConfidence += toNumber(
            record.confidence,
            0
        );

        if (
            String(
                record.risk
            ).toLowerCase()
            === "high"
        ) {
            highRiskCount++;
        }

    });


    const averageReward =
        totalDecisions > 0
            ? totalReward /
              totalDecisions
            : 0;


    const averageConfidence =
        totalDecisions > 0
            ? totalConfidence /
              totalDecisions
            : 0;


    setText(
        totalDecisions,
        "totalDecisions",
        "historyTotalDecisions"
    );


    setText(
        formatNumber(
            averageReward,
            2
        ),
        "historyAverageReward",
        "averageHistoryReward"
    );


    setText(
        formatPercentage(
            averageConfidence
        ),
        "historyAverageConfidence",
        "averageHistoryConfidence"
    );


    setText(
        highRiskCount,
        "highRiskDecisions",
        "historyHighRisk"
    );
}


/* =========================================================
   Export History
   ========================================================= */

function exportHistoryCSV() {
    const records =
        appState.filteredHistory.length
            ? appState.filteredHistory
            : appState.history;

    if (!records.length) {
        showMessage("There is no history to export.", "warning");
        return;
    }

    const headers = [
        "Task",
        "Action",
        "Confidence",
        "Risk",
        "Reward",
        "Date"
    ];

    const rows = records.map(record => [
        record.task ??
        record.task_description ??
        "",

        record.action ??
        record.decision ??
        "",

        record.confidence ??
        record.confidence_score ??
        "",

        record.risk ??
        record.risk_level ??
        "",

        record.reward ??
        record.reward_score ??
        "",

        record.created_at ??
        record.timestamp ??
        record.date ??
        ""
    ]);

    const csv = [headers, ...rows]
        .map(row =>
            row
                .map(value =>
                    `"${String(value ?? "").replaceAll('"', '""')}"`
                )
                .join(",")
        )
        .join("\n");

    const blob = new Blob([csv], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download =
        `eada-history-${new Date().toISOString().slice(0, 10)}.csv`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);

    showMessage("History exported successfully.", "success");
}


/* =========================================================
   Refresh Buttons
   ========================================================= */

function initializeRefreshButtons() {
    const refreshHistoryButton = getElement(
        "refreshHistoryBtn",
        "historyRefreshBtn"
    );

    const refreshDashboardButton = getElement(
        "refreshDashboardBtn",
        "refreshBtn"
    );

    refreshHistoryButton?.addEventListener(
        "click",
        loadHistory
    );

    refreshDashboardButton?.addEventListener(
        "click",
        loadDashboardData
    );
}


/* =========================================================
   Initial Dashboard Loading
   ========================================================= */

async function loadDashboardData() {
    await Promise.allSettled([
        loadAnalytics(),
        loadHistory()
    ]);
}