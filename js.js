// Initialize accounts
const accounts = [
    {
        username: 'usuario1',
        password: '1234',
        balance: 5000.00,
        transactions: [
            { id: 1, type: 'deposit', amount: 5000.00, date: formatDate(new Date()), description: 'Initial deposit' }
        ],
        loans: []
    },
    {
        username: 'usuario2',
        password: '1234',
        balance: 3000.00,
        transactions: [
            { id: 2, type: 'deposit', amount: 3000.00, date: formatDate(new Date()), description: 'Initial deposit' }
        ],
        loans: []
    }
];

let currentUser = null;

// Helper functions
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', { 
        style: 'currency', 
        currency: 'USD',
        minimumFractionDigits: 2 
    }).format(amount);
}

function updateBalanceDisplay() {
    const balanceDisplay = document.getElementById('balance-display');
    balanceDisplay.textContent = formatCurrency(currentUser.account.balance);
}

function renderTransactions() {
    const transactionsList = document.getElementById('transactions-list');
    transactionsList.innerHTML = '';
    
    const transactions = [...currentUser.account.transactions].reverse();
    document.getElementById('transaction-count').textContent = 
        `Últimas ${transactions.length} transacciones`;
    
    transactions.forEach(transaction => {
        const transactionTypeClass = 
            transaction.type === 'transfer_in' ? 'transaction-in' :
            transaction.type === 'loan' ? 'transaction-loan' :
            transaction.type === 'tax' ? 'transaction-tax' :
            transaction.type === 'loan_payment' ? 'transaction-payment' : 'transaction-out';
        
        const icon = 
            transaction.type === 'transfer_in' ? '<svg data-lucide="arrow-down-circle" class="transaction-icon ' + transactionTypeClass + '"></svg>' :
            transaction.type === 'transfer_out' ? '<svg data-lucide="arrow-up-circle" class="transaction-icon ' + transactionTypeClass + '"></svg>' :
            transaction.type === 'tax' ? '<svg data-lucide="calculator" class="transaction-icon ' + transactionTypeClass + '"></svg>' :
            '<svg data-lucide="credit-card" class="transaction-icon ' + transactionTypeClass + '"></svg>';
        
        const description = 
            transaction.type === 'transfer_in' ? `Transferencia recibida de ${transaction.sender}` :
            transaction.type === 'transfer_out' ? `Transferencia a ${transaction.recipient}` :
            transaction.type === 'tax' ? 'Pago de impuestos' :
            transaction.type === 'loan' ? 'Préstamo aprobado' :
            transaction.type === 'loan_payment' ? 'Abono a préstamo' :
            transaction.description;
        
        const amountDisplay = 
            transaction.type === 'transfer_in' ? `+${formatCurrency(Math.abs(transaction.amount))}` :
            formatCurrency(Math.abs(transaction.amount));
        
        const transactionElement = document.createElement('li');
        transactionElement.className = 'transaction-item';
        transactionElement.innerHTML = `
            <div class="transaction-details">
                ${icon}
                <div>
                    <p class="transaction-description">${description}</p>
                    <p class="transaction-date">${transaction.date}</p>
                </div>
            </div>
            <span class="transaction-amount ${transactionTypeClass}">
                ${amountDisplay}
            </span>
        `;
        transactionsList.appendChild(transactionElement);
    });
    
    lucide.createIcons();
}

function renderLoans() {
    const loansContainer = document.getElementById('loans-container');
    const loansList = document.getElementById('loans-list');
    const loans = currentUser.account.loans;
    
    if (loans.length === 0) {
        loansContainer.classList.add('hidden');
        loansList.innerHTML = '';
        return;
    }
    
    loansContainer.classList.remove('hidden');
    loansList.innerHTML = '';
    
    loans.forEach(loan => {
        const progress = ((loan.amount - loan.remaining) / loan.amount) * 100;
        const loanElement = document.createElement('div');
        loanElement.className = 'loan-item';
        loanElement.innerHTML = `
            <div class="loan-header">
                <span class="loan-amount">${formatCurrency(loan.amount)}</span>
                <span class="loan-progress">${progress.toFixed(0)}% pagado</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: ${progress}%"></div>
            </div>
            <p class="loan-info">
                Cuota mensual: ${formatCurrency(loan.monthlyPayment)}
            </p>
        `;
        loansList.appendChild(loanElement);
    });
}

// Core functionality
function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    const user = accounts.find(u => 
        u.username === username && u.password === password
    );
    
    if (user) {
        currentUser = { ...user, account: { ...user } };
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        document.getElementById('current-user').textContent = currentUser.username;
        updateBalanceDisplay();
        renderTransactions();
        renderLoans();
    } else {
        alert('Credenciales inválidas. Intente usuario1/1234 o usuario2/1234');
    }
}

function handleLogout() {
    currentUser = null;
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('dashboard-screen').classList.add('hidden');
}

function transferFunds(event) {
    event.preventDefault();
    const amount = parseFloat(document.getElementById('transferAmount').value);
    const recipientUsername = document.getElementById('recipient').value;
    
    if (isNaN(amount) || amount <= 0) {
        alert('Monto inválido');
        return;
    }
    
    const recipient = accounts.find(a => a.username === recipientUsername);
    if (!recipient) {
        alert('Destinatario no encontrado');
        return;
    }
    
    if (currentUser.account.balance < amount) {
        alert('Fondos insuficientes');
        return;
    }
    
    // Update sender
    const newSenderBalance = currentUser.account.balance - amount;
    const newSenderTransactions = [
        ...currentUser.account.transactions,
        {
            id: Date.now(),
            type: 'transfer_out',
            amount,
            date: formatDate(new Date()),
            recipient: recipientUsername
        }
    ];
    
    // Update recipient
    const newRecipientBalance = recipient.balance + amount;
    const newRecipientTransactions = [
        ...recipient.transactions,
        {
            id: Date.now() + 1,
            type: 'transfer_in',
            amount,
            date: formatDate(new Date()),
            sender: currentUser.username
        }
    ];
    
    // Update accounts
    accounts.forEach(account => {
        if (account.username === currentUser.username) {
            account.balance = newSenderBalance;
            account.transactions = newSenderTransactions;
        }
        if (account.username === recipientUsername) {
            account.balance = newRecipientBalance;
            account.transactions = newRecipientTransactions;
        }
    });
    
    // Update current user
    currentUser.account.balance = newSenderBalance;
    currentUser.account.transactions = newSenderTransactions;
    
    // Reset form
    document.getElementById('transferAmount').value = '';
    
    // Update UI
    updateBalanceDisplay();
    renderTransactions();
    alert(`Transferencia de ${formatCurrency(amount)} realizada con éxito`);
}

function applyLoan(event) {
    event.preventDefault();
    const amount = parseFloat(document.getElementById('loanAmount').value);
    
    if (isNaN(amount) || amount <= 0) {
        alert('Monto de préstamo inválido');
        return;
    }
    
    const newLoan = {
        id: Date.now(),
        amount,
        monthlyPayment: amount * 0.05,
        remaining: amount,
        startDate: formatDate(new Date())
    };
    
    // Update user account
    const newBalance = currentUser.account.balance + amount;
    const newTransactions = [
        ...currentUser.account.transactions,
        {
            id: Date.now() + 2,
            type: 'loan',
            amount,
            date: formatDate(new Date()),
            description: `Préstamo aprobado - Cuota mensual: ${formatCurrency(amount * 0.05)}`
        }
    ];
    
    // Update accounts
    accounts.forEach(account => {
        if (account.username === currentUser.username) {
            account.balance = newBalance;
            account.transactions = newTransactions;
            account.loans = [...account.loans, newLoan];
        }
    });
    
    // Update current user
    currentUser.account.balance = newBalance;
    currentUser.account.transactions = newTransactions;
    currentUser.account.loans = [...currentUser.account.loans, newLoan];
    
    // Reset form
    document.getElementById('loanAmount').value = '';
    
    // Update UI
    updateBalanceDisplay();
    renderTransactions();
    renderLoans();
    alert(`Préstamo de ${formatCurrency(amount)} aprobado con éxito`);
}

function processMonthlyCharges() {
    const taxRate = 0.08; // 8% de impuestos
    
    // Calculate tax
    const taxAmount = currentUser.account.balance * taxRate;
    const newBalanceAfterTax = currentUser.account.balance - taxAmount;
    
    // Process loans
    let balanceAfterLoans = newBalanceAfterTax;
    const updatedLoans = [...currentUser.account.loans];
    const newTransactions = [...currentUser.account.transactions];
    
    updatedLoans.forEach((loan, index) => {
        const payment = Math.min(loan.monthlyPayment, loan.remaining);
        balanceAfterLoans -= payment;
        updatedLoans[index].remaining -= payment;
        
        if (payment > 0) {
            newTransactions.push({
                id: Date.now() + loan.id,
                type: 'loan_payment',
                amount: payment,
                date: formatDate(new Date()),
                description: `Abono a préstamo #${loan.id}`
            });
        }
    });
    
    // Update accounts
    accounts.forEach(account => {
        if (account.username === currentUser.username) {
            account.balance = balanceAfterLoans;
            account.transactions = [
                ...account.transactions,
                {
                    id: Date.now(),
                    type: 'tax',
                    amount: taxAmount,
                    date: formatDate(new Date()),
                    description: `Impuestos mensuales (${(taxRate * 100).toFixed(0)}%)`
                }
            ];
            account.loans = updatedLoans.filter(loan => loan.remaining > 0);
        }
    });
    
    // Update current user
    currentUser.account.balance = balanceAfterLoans;
    currentUser.account.transactions = [
        ...currentUser.account.transactions,
        {
            id: Date.now(),
            type: 'tax',
            amount: taxAmount,
            date: formatDate(new Date()),
            description: `Impuestos mensuales (${(taxRate * 100).toFixed(0)}%)`
        }
    ];
    currentUser.account.loans = updatedLoans.filter(loan => loan.remaining > 0);
    
    // Update UI
    updateBalanceDisplay();
    renderTransactions();
    renderLoans();
    alert('Procesamiento mensual completado: Impuestos y pagos de préstamos aplicados');
}

function generateStatement() {
    // Show only last 10 transactions
    accounts.forEach(account => {
        if (account.username === currentUser.username) {
            account.transactions = account.transactions.slice(-10);
        }
    });
    
    currentUser.account.transactions = currentUser.account.transactions.slice(-10);
    renderTransactions();
    alert('Estado de cuenta generado con las últimas 10 transacciones');
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-button').addEventListener('click', handleLogout);
    document.getElementById('transfer-form').addEventListener('submit', transferFunds);
    document.getElementById('loan-form').addEventListener('submit', applyLoan);
    document.getElementById('process-monthly').addEventListener('click', processMonthlyCharges);
    document.getElementById('generate-statement').addEventListener('click', generateStatement);
    
    // Initialize icons
    lucide.createIcons();
});