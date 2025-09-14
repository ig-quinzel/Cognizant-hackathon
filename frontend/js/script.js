document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // --- Page Routing / Logic ---
    const pageId = document.body.querySelector('div[id$="-page"], div[id$="-container"]')?.id || '';

    // Login Page Logic
    if (pageId.startsWith('login')) {
        const loginButton = document.getElementById('login-button');
        if (loginButton) {
            loginButton.addEventListener('click', () => {
                // In a real app, you'd perform authentication here
                window.location.href = 'dashboard.html';
            });
        }
    }

    // Main App Logic (for all pages except login)
    if (pageId.startsWith('app-container')) {
        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                window.location.href = 'login.html';
            });
        }
    }

    // Dashboard Page Logic
    if (document.getElementById('dashboard-page-content')) {
        renderDashboardCharts();
    }

    // Prediction Page Logic
    if (document.getElementById('prediction-page-container')) {
        setupPredictionPage();
    }

    // Data Management Page Logic
    if (document.getElementById('data-page-content')) {
        setupDataManagementPage();
    }

    // --- Function Definitions ---

    function setupPredictionPage() {
        const predictionFormContent = document.getElementById('prediction-form-content');
        const predictionResultsContent = document.getElementById('prediction-results-content');
        const generatePredictionBtn = document.getElementById('generate-prediction-btn');
        const newPredictionBtn = document.getElementById('new-prediction-btn');
        const predictionError = document.getElementById('prediction-error');
        const formInputs = {
            itemName: document.getElementById('item-name'),
            category: document.getElementById('category'),
            histPrice: document.getElementById('hist-price'),
            marketDemand: document.getElementById('market-demand'),
            seasonalFactor: document.getElementById('seasonal-factor')
        };

        generatePredictionBtn.addEventListener('click', () => {
            const allFilled = Object.values(formInputs).every(input => input.value.trim() !== '');
            if (!allFilled) {
                predictionError.classList.remove('hidden');
                return;
            }
            predictionError.classList.add('hidden');

            const btnText = generatePredictionBtn.querySelector('.btn-text');
            btnText.textContent = 'Generating...';
            generatePredictionBtn.disabled = true;
            const spinner = document.createElement('i');
            spinner.setAttribute('data-lucide', 'loader-2');
            spinner.classList.add('w-5', 'h-5', 'animate-spin');
            generatePredictionBtn.prepend(spinner);
            lucide.createIcons({ nodes: [spinner] });

            setTimeout(() => {
                const histPrice = parseFloat(formInputs.histPrice.value);
                const predictedPrice = histPrice * 0.92;
                const priceChange = ((predictedPrice - histPrice) / histPrice) * 100;

                document.getElementById('result-item-name').textContent = formInputs.itemName.value;
                document.getElementById('result-price').textContent = '$' + predictedPrice.toFixed(2);
                document.getElementById('result-confidence').textContent = (Math.random() * (98 - 75) + 75).toFixed(2) + '% Confidence';
                document.getElementById('result-hist-price').textContent = '$' + histPrice.toFixed(2);
                
                const priceChangeEl = document.getElementById('result-price-change');
                priceChangeEl.textContent = priceChange.toFixed(1) + '%';
                priceChangeEl.classList.toggle('text-red-500', priceChange < 0);
                priceChangeEl.classList.toggle('text-green-500', priceChange >= 0);

                document.getElementById('result-category').textContent = formInputs.category.value;
                document.getElementById('result-demand').textContent = formInputs.marketDemand.value + '/10';
                document.getElementById('result-season').textContent = formInputs.seasonalFactor.options[formInputs.seasonalFactor.selectedIndex].text;
                
                document.getElementById('market-analysis-text').textContent = `The ${formInputs.itemName.value} has seen stable global demand, but with a rating of ${formInputs.marketDemand.value}/10 in market demand, it indicates moderate interest. The seasonal factor suggests a mild impact on pricing. Historical pricing shows a solid base at $${histPrice.toFixed(2)}, but a predicted decline to $${predictedPrice.toFixed(2)} factors in current market saturation and lower new model demand.`;

                predictionFormContent.classList.add('hidden');
                predictionResultsContent.classList.remove('hidden');

                btnText.textContent = 'Generate Prediction';
                generatePredictionBtn.disabled = false;
                generatePredictionBtn.querySelector('i').remove();
            }, 2000);
        });

        newPredictionBtn.addEventListener('click', () => {
            predictionResultsContent.classList.add('hidden');
            predictionFormContent.classList.remove('hidden');
            predictionError.classList.add('hidden');
        });
    }

    function setupDataManagementPage() {
        const fileUpload = document.getElementById('file-upload');
        const fileUploadText = document.getElementById('file-upload-text');
        if (fileUpload) {
            fileUpload.addEventListener('change', () => {
                if (fileUpload.files.length > 0) {
                    fileUploadText.textContent = fileUpload.files[0].name;
                } else {
                    fileUploadText.textContent = 'Upload CSV or Excel File';
                }
            });
        }
    }

    function renderDashboardCharts() {
        let barChartInstance, pieChartInstance;

        const barCtx = document.getElementById('barChart')?.getContext('2d');
        if (barCtx) {
            barChartInstance = new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: ['Nike Air Jordan', 'MacBook Pro M3', 'iPhone 15 Pro'],
                    datasets: [{
                        label: 'Predicted Price',
                        data: [220, 2550, 1100],
                        backgroundColor: 'rgba(79, 70, 229, 0.8)',
                        borderRadius: 8,
                        barThickness: 30,
                    }, {
                        label: 'Market Average',
                        data: [250, 2600, 1150],
                        backgroundColor: 'rgba(203, 213, 225, 0.8)',
                        borderRadius: 8,
                        barThickness: 30,
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });
        }

        const pieCtx = document.getElementById('pieChart')?.getContext('2d');
        if (pieCtx) {
            pieChartInstance = new Chart(pieCtx, {
                type: 'pie',
                data: {
                    labels: ['Electronics', 'Clothing', 'Food', 'Automotive'],
                    datasets: [{
                        data: [50, 17, 17, 17],
                        backgroundColor: ['#4f46e5', '#a78bfa', '#34d399', '#f59e0b'],
                        borderColor: '#ffffff',
                        borderWidth: 4,
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
            });
        }
    }
});
