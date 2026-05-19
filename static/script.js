document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');

    function switchView(targetId) {
        navBtns.forEach(btn => btn.classList.remove('active'));
        views.forEach(view => view.classList.remove('active'));
        
        const activeBtn = document.querySelector(`[data-target="${targetId}"]`);
        if (activeBtn) activeBtn.classList.add('active');
        
        const activeView = document.getElementById(targetId);
        if (activeView) activeView.classList.add('active');
    }

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            if (target === 'dashboard-view') {
                loadClients();
            } else if (target === 'add-client-view') {
                resetClientForm();
            }
            switchView(target);
        });
    });

    // --- Dashboard ---
    async function loadClients() {
        const grid = document.getElementById('clients-grid');
        grid.innerHTML = '<div class="loading">Loading clients...</div>';
        
        try {
            const res = await fetch('/api/clients');
            const clients = await res.json();
            
            if (clients.length === 0) {
                grid.innerHTML = '<p class="text-sm">No clients found. Add your first client to get started.</p>';
                return;
            }
            
            grid.innerHTML = '';
            clients.forEach(client => {
                const card = document.createElement('div');
                card.className = 'client-card';
                let totalSalary = (client.salary_client1 || 0) + (client.salary_client2 || 0);
                card.innerHTML = `
                    <div class="client-card-header">
                        <div class="client-name">${client.name} ${client.is_joint && client.spouse_name ? '& ' + client.spouse_name : ''}</div>
                        <div class="client-badge">Client</div>
                    </div>
                    <div class="text-sm">
                        Total Inflow: $${totalSalary.toLocaleString()}<br>
                        Budget: $${client.expense_budget ? client.expense_budget.toLocaleString() : '0'}
                    </div>
                    <div class="client-actions">
                        <button class="btn btn-primary btn-sm generate-report-trigger" data-id="${client.id}">Generate Report</button>
                        <button class="btn btn-secondary btn-sm edit-client-trigger" data-id="${client.id}">Edit</button>
                    </div>
                `;
                grid.appendChild(card);
            });

            document.querySelectorAll('.generate-report-trigger').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    openGenerateReport(id);
                });
            });

            document.querySelectorAll('.edit-client-trigger').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    openEditClient(id);
                });
            });

        } catch (err) {
            console.error(err);
            grid.innerHTML = '<p style="color:red">Error loading clients.</p>';
        }
    }

    // --- Client Form ---
    const clientForm = document.getElementById('client-form');
    const accountsContainer = document.getElementById('accounts-container');
    const addAccountBtn = document.getElementById('add-account-btn');
    const isJointToggle = document.getElementById('is_joint');
    const spouseSection = document.getElementById('spouse-section');

    isJointToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            spouseSection.classList.remove('hidden');
        } else {
            spouseSection.classList.add('hidden');
        }
    });

    function createAccountRow(acc = {}) {
        const row = document.createElement('div');
        row.className = 'account-row';
        
        let ownerVal = acc.owner || 'client1';
        let catVal = acc.category || 'non_retirement';

        row.innerHTML = `
            <select class="acc-owner">
                <option value="client1" ${ownerVal==='client1'?'selected':''}>Client 1</option>
                <option value="client2" ${ownerVal==='client2'?'selected':''}>Client 2</option>
                <option value="joint" ${ownerVal==='joint'?'selected':''}>Joint</option>
            </select>
            <select class="acc-category">
                <option value="retirement" ${catVal==='retirement'?'selected':''}>Retirement</option>
                <option value="non_retirement" ${catVal==='non_retirement'?'selected':''}>Non-Retirement</option>
                <option value="trust" ${catVal==='trust'?'selected':''}>Trust / Property</option>
                <option value="liability" ${catVal==='liability'?'selected':''}>Liability</option>
            </select>
            <input type="text" placeholder="Institution (e.g. Schwab)" class="acc-institution" value="${acc.institution || ''}" required>
            <input type="text" placeholder="Type (e.g. Roth IRA)" class="acc-type" value="${acc.acc_type || ''}">
            <input type="text" placeholder="Last 4" class="acc-last4" maxlength="4" value="${acc.last4 || ''}">
            
            <!-- Dynamic extra field -->
            <input type="number" placeholder="Int. Rate %" class="acc-rate ${catVal==='liability'?'':'hidden'}" step="0.01" value="${acc.interest_rate || ''}">
            
            <button type="button" class="delete-btn" title="Remove Account">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
        `;
        
        const catSelect = row.querySelector('.acc-category');
        const rateInput = row.querySelector('.acc-rate');

        catSelect.addEventListener('change', (e) => {
            if (e.target.value === 'liability') {
                rateInput.classList.remove('hidden');
            } else {
                rateInput.classList.add('hidden');
            }
        });

        row.querySelector('.delete-btn').addEventListener('click', () => {
            row.remove();
        });
        return row;
    }

    addAccountBtn.addEventListener('click', () => {
        accountsContainer.appendChild(createAccountRow());
    });

    function resetClientForm() {
        clientForm.reset();
        document.getElementById('client_id').value = '';
        document.getElementById('client-form-title').innerText = 'New Client Setup';
        spouseSection.classList.add('hidden');
        accountsContainer.innerHTML = '';
        accountsContainer.appendChild(createAccountRow()); 
    }

    async function openEditClient(id) {
        try {
            const res = await fetch(`/api/clients/${id}`);
            const client = await res.json();
            
            document.getElementById('client_id').value = client.id;
            document.getElementById('is_joint').checked = client.is_joint ? true : false;
            
            if (client.is_joint) {
                spouseSection.classList.remove('hidden');
            } else {
                spouseSection.classList.add('hidden');
            }

            document.getElementById('name').value = client.name || '';
            document.getElementById('dob').value = client.dob || '';
            document.getElementById('ssn_last4').value = client.ssn_last4 || '';
            document.getElementById('salary_client1').value = client.salary_client1 || '';
            
            document.getElementById('spouse_name').value = client.spouse_name || '';
            document.getElementById('spouse_dob').value = client.spouse_dob || '';
            document.getElementById('spouse_ssn_last4').value = client.spouse_ssn_last4 || '';
            document.getElementById('salary_client2').value = client.salary_client2 || '';
            
            document.getElementById('expense_budget').value = client.expense_budget || '';
            document.getElementById('insurance_deductibles').value = client.insurance_deductibles || '';

            accountsContainer.innerHTML = '';
            if (client.accounts && client.accounts.length > 0) {
                client.accounts.forEach(acc => {
                    accountsContainer.appendChild(createAccountRow(acc));
                });
            } else {
                accountsContainer.appendChild(createAccountRow());
            }
            
            document.getElementById('client-form-title').innerText = `Edit ${client.name}`;
            switchView('add-client-view');
        } catch (e) {
            console.error("Error loading client", e);
        }
    }

    clientForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const accounts = [];
        accountsContainer.querySelectorAll('.account-row').forEach(row => {
            accounts.push({
                owner: row.querySelector('.acc-owner').value,
                category: row.querySelector('.acc-category').value,
                institution: row.querySelector('.acc-institution').value,
                acc_type: row.querySelector('.acc-type').value,
                last4: row.querySelector('.acc-last4').value,
                interest_rate: parseFloat(row.querySelector('.acc-rate').value) || 0,
                address: ''
            });
        });

        const data = {
            is_joint: document.getElementById('is_joint').checked,
            name: document.getElementById('name').value,
            dob: document.getElementById('dob').value,
            ssn_last4: document.getElementById('ssn_last4').value,
            salary_client1: parseFloat(document.getElementById('salary_client1').value) || 0,
            spouse_name: document.getElementById('spouse_name').value,
            spouse_dob: document.getElementById('spouse_dob').value,
            spouse_ssn_last4: document.getElementById('spouse_ssn_last4').value,
            salary_client2: parseFloat(document.getElementById('salary_client2').value) || 0,
            expense_budget: parseFloat(document.getElementById('expense_budget').value) || 0,
            insurance_deductibles: parseFloat(document.getElementById('insurance_deductibles').value) || 0,
            accounts: accounts
        };

        const id = document.getElementById('client_id').value;
        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/clients/${id}` : '/api/clients';

        try {
            await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            switchView('dashboard-view');
            loadClients();
        } catch (e) {
            console.error("Error saving client", e);
            alert("Error saving client data.");
        }
    });

    document.getElementById('cancel-client-btn').addEventListener('click', () => {
        switchView('dashboard-view');
        loadClients();
    });

    // --- Generate Report ---
    const reportForm = document.getElementById('report-form');
    const balancesContainer = document.getElementById('balances-container');
    let currentReportClient = null;

    async function openGenerateReport(id) {
        try {
            const res = await fetch(`/api/clients/${id}`);
            currentReportClient = await res.json();
            
            document.getElementById('report_client_id').value = id;
            document.getElementById('report-client-name').innerText = `Client: ${currentReportClient.name}`;
            document.getElementById('report_date').valueAsDate = new Date();
            
            document.getElementById('report-results').classList.add('hidden');
            
            balancesContainer.innerHTML = '';
            
            if (!currentReportClient.accounts || currentReportClient.accounts.length === 0) {
                balancesContainer.innerHTML = '<p>No accounts configured for this client.</p>';
            } else {
                currentReportClient.accounts.forEach(acc => {
                    const group = document.createElement('div');
                    group.className = 'account-row'; // Reuse styles
                    group.style.display = 'grid';
                    group.style.gridTemplateColumns = "2fr 1fr 1fr";
                    group.style.backgroundColor = "transparent";
                    group.style.border = "none";
                    group.style.padding = "0";
                    group.style.marginBottom = "0.5rem";
                    
                    let labelText = `${acc.institution || ''} ${acc.acc_type || ''} ${acc.last4 ? '(*' + acc.last4 + ')' : ''}`;
                    let isInvestment = (acc.category === 'retirement' || acc.category === 'non_retirement');
                    
                    group.innerHTML = `
                        <div style="display:flex; flex-direction:column; justify-content:center;">
                            <label style="font-size: 1rem;">${labelText}</label>
                            <span class="text-sm" style="margin:0;">Category: ${acc.category} | Owner: ${acc.owner}</span>
                        </div>
                        <input type="number" step="0.01" class="acc-balance-input" data-id="${acc.id}" value="${acc.last_known_balance || 0}" required placeholder="Balance">
                        ${isInvestment ? `<input type="number" step="0.01" class="acc-cash-input" data-id="${acc.id}" value="${acc.cash_balance || 0}" placeholder="Cash Bal">` : `<div></div>`}
                    `;
                    balancesContainer.appendChild(group);
                });
            }
            
            switchView('generate-report-view');
        } catch (e) {
            console.error("Error loading for report", e);
        }
    }

    reportForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const balances = [];
        balancesContainer.querySelectorAll('.account-row').forEach(row => {
            const balInput = row.querySelector('.acc-balance-input');
            const cashInput = row.querySelector('.acc-cash-input');
            if (balInput) {
                balances.push({
                    id: balInput.getAttribute('data-id'),
                    balance: parseFloat(balInput.value) || 0,
                    cash_balance: cashInput ? (parseFloat(cashInput.value) || 0) : 0
                });
            }
        });

        const payload = {
            client_id: document.getElementById('report_client_id').value,
            date: document.getElementById('report_date').value,
            balances: balances
        };

        const generateBtn = document.getElementById('generate-btn');
        generateBtn.innerText = 'Generating...';
        generateBtn.disabled = true;

        try {
            const res = await fetch('/api/generate-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) throw new Error("Failed generation");
            
            const data = await res.json();
            
            document.getElementById('sacs-download').href = data.sacs_url;
            document.getElementById('tcc-download').href = data.tcc_url;
            
            document.getElementById('report-results').classList.remove('hidden');
        } catch (e) {
            console.error("Error generating reports", e);
            alert("Failed to generate reports.");
        } finally {
            generateBtn.innerText = 'Generate PDFs';
            generateBtn.disabled = false;
        }
    });

    document.getElementById('cancel-report-btn').addEventListener('click', () => {
        switchView('dashboard-view');
        loadClients();
    });

    // Init
    loadClients();
});
