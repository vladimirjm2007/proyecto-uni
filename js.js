// ------------- INICIALIZACIÓN DE DATOS SIMULADOS DE USUARIOS -------------

// Este arreglo contiene dos cuentas de usuario de ejemplo.
// Cada cuenta tiene usuario, contraseña, saldo, lista de transacciones y préstamos.
const accounts = [
    {
        username: 'usuario1', // Identificador único del usuario
        password: '1234',     // Contraseña para autenticarse
        balance: 5000.00,     // Saldo inicial al crear la cuenta
        transactions: [       // Historial de movimientos, inicia con el depósito inicial
            { id: 1, type: 'deposit', amount: 5000.00, date: formatDate(new Date()), description: 'Initial deposit' }
        ],
        loans: []             // Préstamos solicitados por el usuario (vacío al inicio)
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

// Variable global que almacena el usuario que está actualmente logueado.
// Sirve para saber a quién se le deben aplicar los cambios y mostrar la información.
let currentUser = null;

// ------------- FUNCIONES AUXILIARES PARA FORMATO Y INTERFAZ -------------

// Recibe un objeto Date y devuelve un string en formato 'YYYY-MM-DD'.
// Es útil para mostrar fechas uniformes en las transacciones y préstamos.
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Añade cero si el mes es menor a 10
    const day = String(date.getDate()).padStart(2, '0');        // Añade cero si el día es menor a 10
    return `${year}-${month}-${day}`;
}

// Da formato de moneda USD a cualquier número recibido.
// Ejemplo: 5000 => "$5,000.00 USD"
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', { 
        style: 'currency', 
        currency: 'USD',
        minimumFractionDigits: 2 
    }).format(amount);
}

// Actualiza el texto que muestra el saldo en el panel principal con el saldo del usuario actual.
function updateBalanceDisplay() {
    const balanceDisplay = document.getElementById('balance-display');
    // Siempre se usa el formato de moneda para mayor claridad al usuario
    balanceDisplay.textContent = formatCurrency(currentUser.account.balance);
}

// Renderiza la lista de transacciones del usuario actual en pantalla.
// Incluye íconos, descripciones y colores según el tipo de transacción.
function renderTransactions() {
    const transactionsList = document.getElementById('transactions-list');
    // Limpia la lista para evitar duplicados al refrescar
    transactionsList.innerHTML = '';
    
    // Se invierte el orden para mostrar primero las más recientes
    const transactions = [...currentUser.account.transactions].reverse();
    // Muestra la cantidad de transacciones en el encabezado
    document.getElementById('transaction-count').textContent = 
        `Últimas ${transactions.length} transacciones`;
    
    // Por cada transacción, determina su estilo, ícono y descripción específica
    transactions.forEach(transaction => {
        // Selecciona la clase CSS según el tipo de movimiento (entrada, salida, préstamo, impuesto, etc.)
        const transactionTypeClass = 
            transaction.type === 'transfer_in' ? 'transaction-in' :
            transaction.type === 'loan' ? 'transaction-loan' :
            transaction.type === 'tax' ? 'transaction-tax' :
            transaction.type === 'loan_payment' ? 'transaction-payment' : 'transaction-out';
        
        // Elige el ícono visual para cada tipo de transacción usando SVGs
        const icon = 
            transaction.type === 'transfer_in' ? '<svg data-lucide="arrow-down-circle" class="transaction-icon ' + transactionTypeClass + '"></svg>' :
            transaction.type === 'transfer_out' ? '<svg data-lucide="arrow-up-circle" class="transaction-icon ' + transactionTypeClass + '"></svg>' :
            transaction.type === 'tax' ? '<svg data-lucide="calculator" class="transaction-icon ' + transactionTypeClass + '"></svg>' :
            '<svg data-lucide="credit-card" class="transaction-icon ' + transactionTypeClass + '"></svg>';
        
        // Personaliza el mensaje según el tipo de movimiento
        const description = 
            transaction.type === 'transfer_in' ? `Transferencia recibida de ${transaction.sender}` :
            transaction.type === 'transfer_out' ? `Transferencia a ${transaction.recipient}` :
            transaction.type === 'tax' ? 'Pago de impuestos' :
            transaction.type === 'loan' ? 'Préstamo aprobado' :
            transaction.type === 'loan_payment' ? 'Abono a préstamo' :
            transaction.description;
        
        // Si es transferencia recibida, muestra el monto con "+" delante
        const amountDisplay = 
            transaction.type === 'transfer_in' ? `+${formatCurrency(Math.abs(transaction.amount))}` :
            formatCurrency(Math.abs(transaction.amount));
        
        // Crea el elemento visual de la transacción y lo agrega a la lista
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
    
    // Inicializa los íconos SVG (Lucide) para que se vean en pantalla
    lucide.createIcons();
}

// Renderiza la lista de préstamos activos del usuario actual
// Muestra el monto total, progreso de pago y cuota mensual
function renderLoans() {
    const loansContainer = document.getElementById('loans-container');
    const loansList = document.getElementById('loans-list');
    const loans = currentUser.account.loans;
    
    // Si no hay préstamos, oculta la sección para ahorrar espacio
    if (loans.length === 0) {
        loansContainer.classList.add('hidden');
        loansList.innerHTML = '';
        return;
    }
    
    // Si sí hay, la muestra y limpia la lista antes de renderizar
    loansContainer.classList.remove('hidden');
    loansList.innerHTML = '';
    
    loans.forEach(loan => {
        // Calcula el porcentaje pagado del préstamo
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

// ------------- ACCIONES PRINCIPALES DEL USUARIO -------------

// Procesa el formulario de login y verifica usuario y contraseña
function handleLogin(event) {
    event.preventDefault(); // Evita que el formulario recargue la página
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Busca el usuario con esas credenciales en la lista de cuentas
    const user = accounts.find(u => 
        u.username === username && u.password === password
    );
    
    if (user) {
        // Si existe, guarda su info en currentUser y muestra el panel principal
        currentUser = { ...user, account: { ...user } };
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('dashboard-screen').classList.remove('hidden');
        document.getElementById('current-user').textContent = currentUser.username;
        // Muestra los datos relevantes del usuario
        updateBalanceDisplay();
        renderTransactions();
        renderLoans();
    } else {
        // Si no existe, muestra alerta con ayuda para credenciales de prueba
        alert('Credenciales inválidas. Intente usuario1/1234 o usuario2/1234');
    }
}

// Cierra la sesión del usuario y regresa a la pantalla de login
function handleLogout() {
    currentUser = null; // Borra el usuario actual
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('dashboard-screen').classList.add('hidden');
}

// Procesa el formulario para transferir fondos a otro usuario
function transferFunds(event) {
    event.preventDefault();
    const amount = parseFloat(document.getElementById('transferAmount').value);
    const recipientUsername = document.getElementById('recipient').value;
    
    // Validaciones de entrada (monto válido y usuario existente)
    if (isNaN(amount) || amount <= 0) {
        alert('Monto inválido');
        return;
    }
    
    const recipient = accounts.find(a => a.username === recipientUsername);
    if (!recipient) {
        alert('Destinatario no encontrado');
        return;
    }
    
    // Si el saldo es insuficiente, muestra un error
    if (currentUser.account.balance < amount) {
        alert('Fondos insuficientes');
        return;
    }
    
    // 1. Actualiza saldo y transacciones del remitente
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
    
    // 2. Actualiza saldo y transacciones del destinatario
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
    
    // 3. Guarda los cambios en el arreglo de cuentas global
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
    
    // 4. Actualiza datos del usuario actual en memoria
    currentUser.account.balance = newSenderBalance;
    currentUser.account.transactions = newSenderTransactions;
    
    // 5. Limpia el campo del formulario para nueva transferencia
    document.getElementById('transferAmount').value = '';
    
    // 6. Refresca saldo y lista de movimientos en la interfaz
    updateBalanceDisplay();
    renderTransactions();
    alert(`Transferencia de ${formatCurrency(amount)} realizada con éxito`);
}

// Procesa el formulario para solicitar un préstamo
function applyLoan(event) {
    event.preventDefault();
    const amount = parseFloat(document.getElementById('loanAmount').value);
    
    // Validación de monto de préstamo
    if (isNaN(amount) || amount <= 0) {
        alert('Monto de préstamo inválido');
        return;
    }
    
    // Crea el objeto préstamo con cuota fija mensual (5%)
    const newLoan = {
        id: Date.now(),
        amount,
        monthlyPayment: amount * 0.05,
        remaining: amount, // Saldo pendiente por pagar
        startDate: formatDate(new Date())
    };
    
    // Suma el monto del préstamo al saldo del usuario y agrega la transacción de préstamo
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
    
    // Actualiza la información global de la cuenta
    accounts.forEach(account => {
        if (account.username === currentUser.username) {
            account.balance = newBalance;
            account.transactions = newTransactions;
            account.loans = [...account.loans, newLoan];
        }
    });
    
    // Actualiza la información del usuario actual
    currentUser.account.balance = newBalance;
    currentUser.account.transactions = newTransactions;
    currentUser.account.loans = [...currentUser.account.loans, newLoan];
    
    // Limpia el campo del formulario de préstamo
    document.getElementById('loanAmount').value = '';
    
    // Actualiza la interfaz para mostrar los cambios
    updateBalanceDisplay();
    renderTransactions();
    renderLoans();
    alert(`Préstamo de ${formatCurrency(amount)} aprobado con éxito`);
}

// Procesa los cargos mensuales automáticos: impuestos y pagos de préstamos
function processMonthlyCharges() {
    const taxRate = 0.08; // 8% es el porcentaje de impuesto aplicado al saldo
    
    // 1. Calcula y descuenta impuestos del saldo
    const taxAmount = currentUser.account.balance * taxRate;
    const newBalanceAfterTax = currentUser.account.balance - taxAmount;
    
    // 2. Procesa pago mensual de cada préstamo (hasta completar el saldo pendiente)
    let balanceAfterLoans = newBalanceAfterTax;
    const updatedLoans = [...currentUser.account.loans];
    const newTransactions = [...currentUser.account.transactions];
    
    updatedLoans.forEach((loan, index) => {
        // La cuota nunca puede ser mayor que el saldo pendiente
        const payment = Math.min(loan.monthlyPayment, loan.remaining);
        balanceAfterLoans -= payment;
        updatedLoans[index].remaining -= payment;
        
        // Si hubo algún pago, se registra la transacción
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
    
    // 3. Actualiza la cuenta global del usuario con saldo, movimientos e info de préstamos
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
            // Elimina préstamos pagados completamente
            account.loans = updatedLoans.filter(loan => loan.remaining > 0);
        }
    });
    
    // 4. Actualiza también los datos locales del usuario actual
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
    
    // 5. Refresca toda la interfaz para reflejar cambios
    updateBalanceDisplay();
    renderTransactions();
    renderLoans();
    alert('Procesamiento mensual completado: Impuestos y pagos de préstamos aplicados');
}

// Muestra solo las últimas 10 transacciones del usuario (para el estado de cuenta)
function generateStatement() {
    // Limita el historial de transacciones a los últimos 10 movimientos
    accounts.forEach(account => {
        if (account.username === currentUser.username) {
            account.transactions = account.transactions.slice(-10);
        }
    });
    
    currentUser.account.transactions = currentUser.account.transactions.slice(-10);
    renderTransactions();
    alert('Estado de cuenta generado con las últimas 10 transacciones');
}

// ------------- INICIALIZACIÓN DE LA APLICACIÓN Y EVENTOS -------------

// Al cargar la página, conecta los formularios y botones con sus funciones correspondientes
document.addEventListener('DOMContentLoaded', () => {
    // Cuando el usuario envía el formulario de login
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    // Cuando cierra la sesión
    document.getElementById('logout-button').addEventListener('click', handleLogout);
    // Cuando realiza una transferencia
    document.getElementById('transfer-form').addEventListener('submit', transferFunds);
    // Cuando solicita un préstamo
    document.getElementById('loan-form').addEventListener('submit', applyLoan);
    // Cuando procesa cargos mensuales
    document.getElementById('process-monthly').addEventListener('click', processMonthlyCharges);
    // Cuando genera el estado de cuenta
    document.getElementById('generate-statement').addEventListener('click', generateStatement);
    
    // Inicializa los íconos SVG para mostrar los correctos en la interfaz
    lucide.createIcons();
});
