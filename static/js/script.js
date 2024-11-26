let resultadoGuardado = null;  // Variable para almacenar el último resultado

function appendToExpression(value) {
    document.getElementById('expression').value += value;
}

function clearExpression() {
    // Borrar toda la expresión
    document.getElementById('expression').value = '';
    document.getElementById('result').innerText = '';
    document.getElementById('tree').innerHTML = '';
    document.getElementById('tokens-table').innerHTML = '';
    document.getElementById('total-numbers').textContent = '';
    document.getElementById('total-operators').textContent = '';
}

function clearLastDigit() {
    // Borrar el último carácter de la expresión
    const expression = document.getElementById('expression').value;
    document.getElementById('expression').value = expression.slice(0, -1);
}

function calculateTree() {
    let expression = document.getElementById('expression').value;

    // Enviar la expresión al servidor para obtener el árbol y el resultado
    fetch('http://127.0.0.1:5000/tree', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ expression })
    })
    .then(response => response.json())
    .then(data => {
        // Mostrar el árbol de expresión y el resultado
        document.getElementById('tree').innerHTML = data.treeHTML || 'Error al generar el árbol';
        document.getElementById('result').innerText = data.result || 'Error en la expresión';

        // Mostrar tokens
        displayTokens(data.tokens, data.total_numbers, data.total_operators);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'Error al procesar la solicitud';
    });
}

function guardarResultado() {
    const result = document.getElementById('result').innerText;
    if (result && result !== 'Error en la expresión' && result !== 'Error al procesar la solicitud') {
        resultadoGuardado = result;
        alert("Resultado guardado: " + resultadoGuardado);
    } else {
        alert("No hay resultado para guardar.");
    }
}

function insertLastResult() {
    // Verificar si hay un resultado guardado
    if (resultadoGuardado !== null) {
        document.getElementById('expression').value += resultadoGuardado;  // Insertar el último resultado
    } else {
        alert("No hay un resultado guardado.");
    }
}

function displayTokens(tokens, total_numbers, total_operators) {
    const tokensTable = document.getElementById('tokens-table');
    tokensTable.innerHTML = `<tr><th>Token</th><th>Tipo</th></tr>`; // Encabezados de tabla
    
    tokens.forEach(token => {
        const row = document.createElement('tr');
        const tokenCell = document.createElement('td');
        tokenCell.textContent = token[1];

        const typeCell = document.createElement('td');
        // Identificar correctamente el tipo de token
        if (token[0] === 'number') {
            typeCell.textContent = 'Número';
        } else if (token[0] === 'operador suma') {
            typeCell.textContent = 'Operador Suma';
        } else if (token[0] === 'operador resta') {
            typeCell.textContent = 'Operador Resta';
        } else if (token[0] === 'operador multiplicacion') {
            typeCell.textContent = 'Operador Multiplicación';
        } else if (token[0] === 'operador division') {
            typeCell.textContent = 'Operador División';
        } else if (token[0] === 'operator parentesis izquierda') {
            typeCell.textContent = 'Paréntesis Izquierdo';
        } else if (token[0] === 'operador parentesis derecha') {
            typeCell.textContent = 'Paréntesis Derecho';
        } else {
            typeCell.textContent = 'Desconocido';
        }

        row.appendChild(tokenCell);
        row.appendChild(typeCell);
        tokensTable.appendChild(row);
    });
// Mostrar totales
document.getElementById('total-numbers').textContent = `Total Números: ${total_numbers}`;
document.getElementById('total-operators').textContent = `Total Operadores: ${total_operators}`;

}

