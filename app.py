from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)
CORS(app)  # Permite todas las solicitudes CORS desde cualquier origen

# Variable global para guardar el resultado de la última operación
last_result = None

# Definir tokens para PLY
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
)

# Reglas de expresión regular para los tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore = ' \t'  # Ignorar espacios y tabulaciones


def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)  # Convertir a float
    return t


def t_error(t):
    raise SyntaxError(f"Token inválido: {t.value[0]}")
    t.lexer.skip(1)


lexer = lex.lex()

# Definir la gramática y reglas para PLY
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


def p_expression(p):
    '''expr : expr PLUS term
            | expr MINUS term'''
    p[0] = {"type": "add" if p[2] == '+' else "sub", "left": p[1], "right": p[3]}


def p_expression_term(p):
    '''expr : term'''
    p[0] = p[1]


def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor'''
    p[0] = {"type": "mul" if p[2] == '*' else "div", "left": p[1], "right": p[3]}


def p_term_factor(p):
    '''term : factor'''
    p[0] = p[1]


def p_factor_number(p):
    '''factor : NUMBER'''
    p[0] = {"type": "number", "value": p[1]}


def p_factor_parens(p):
    '''factor : LPAREN expr RPAREN'''
    p[0] = p[2]


def p_error(p):
    if p:
        raise SyntaxError(f"Error de sintaxis cerca de '{p.value}' en la posición {p.lexpos}")
    else:
        raise SyntaxError("Error de sintaxis: entrada incompleta o inesperada.")


parser = yacc.yacc()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tree', methods=['POST'])
def tree():
    global last_result
    data = request.get_json()
    expression = data.get('expression')

    # Reemplazar el marcador de resultado si se usa el último resultado
    if expression == "last_result":
        expression = str(last_result) if last_result is not None else "0"

    if not expression:
        return jsonify({'treeHTML': '', 'result': '', 'tokens': [], 'total_numbers': 0, 'total_operators': 0})

    try:
        # Parsear la expresión para construir el árbol
        tree = parser.parse(expression, lexer=lexer)
        tree_html = render_tree(tree)
        result = evaluate_tree(tree)

        # Extraer los tokens y contar números y operadores
        tokens, total_numbers, total_operators = extract_tokens(expression)

        # Guardar el resultado para uso posterior
        last_result = result
    except SyntaxError as e:
        return jsonify({'treeHTML': f'<p>Error: {str(e)}</p>', 'result': '', 'tokens': [], 'total_numbers': 0, 'total_operators': 0})

    return jsonify({
        'treeHTML': tree_html,
        'result': result,
        'tokens': tokens,
        'total_numbers': total_numbers,
        'total_operators': total_operators
    })

def render_tree(node):
    if node["type"] == "number":
        return f'<div class="node">{node["value"]}</div>'
    
    left_html = render_tree(node["left"])
    right_html = render_tree(node["right"])
    operator = "+" if node["type"] == "add" else "-" if node["type"] == "sub" else "*" if node["type"] == "mul" else "/"

    return f'''
    <div class="tree-node">
        <div class="node">{operator}</div>
        <div class="children">
            <div class="child left">{left_html}</div>
            <div class="child right">{right_html}</div>
        </div>
    </div>
    '''


def evaluate_tree(node):
    """Evalúa el árbol y retorna el resultado."""
    if node['type'] == 'number':
        return node['value']
    left = evaluate_tree(node['left'])
    right = evaluate_tree(node['right'])
    if node['type'] == 'add':
        return left + right
    elif node['type'] == 'sub':
        return left - right
    elif node['type'] == 'mul':
        return left * right
    elif node['type'] == 'div':
        return left / right


def extract_tokens(expression):
    """Extrae los tokens de la expresión."""
    tokens = []
    total_numbers = 0
    total_operators = 0
    for char in expression:
        if char.isdigit() or char == '.':
            if tokens and tokens[-1][0] == 'number':
                tokens[-1] = ('number', tokens[-1][1] + char)  # Continuar el número
            else:
                tokens.append(('number', char))
                total_numbers += 1
        elif char in '+':
            tokens.append(('operador suma', char))
            total_operators += 1
        elif char in '-':
            tokens.append(('operador resta', char))
            total_operators += 1
        elif char in '*':
            tokens.append(('operador multiplicacion', char))
            total_operators += 1
        elif char in '/':
            tokens.append(('operador division', char))
            total_operators += 1
        elif char in '(':
            tokens.append(('operador parentesis izquierda', char))
            total_operators += 1
        elif char in ')':
            tokens.append(('operador parentesis derecha', char))
            total_operators += 1
    return tokens, total_numbers, total_operators


if __name__ == '__main__':
    app.run(debug=True)
