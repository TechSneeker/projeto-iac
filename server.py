from flask import Flask, jsonify, render_template_string
from solucionador_recipientes import *

app = Flask(__name__)

@app.route('/')
def index():
    with open('interface_web.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/solve/<algorithm>')
def solve_algorithm(algorithm):
    try:
        if algorithm == 'BFS':
            path, _ = busca_largura_cega(INICIO)
        elif algorithm == 'DFS':
            path, _ = busca_profundidade_cega(INICIO)
        elif algorithm == 'Gulosa':
            path, _ = busca_gulosa(INICIO, heuristica_conservadora)
        elif algorithm == 'A*':
            path, _ = astar(INICIO, heuristica_conservadora)
        else:
            return jsonify({'error': 'Algoritmo não encontrado'}), 400
        
        if path:
            # Converter para formato JSON
            solution = []
            for state, action in path:
                solution.append({
                    'state': list(state),
                    'action': list(action)
                })
            
            return jsonify({
                'success': True,
                'algorithm': algorithm,
                'steps': len(solution),
                'solution': solution
            })
        else:
            return jsonify({'success': False, 'error': 'Sem solução'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Servidor iniciado em: http://localhost:5000")
    app.run(debug=True, port=5000)