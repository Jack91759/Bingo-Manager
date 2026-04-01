from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bingo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(32)

db = SQLAlchemy(app)

# Database Models
class BingoCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(50), unique=True, nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    numbers = db.Column(db.String(200), nullable=False)  # Stored as comma-separated string
    round_number = db.Column(db.Integer, default=1)
    has_bingo = db.Column(db.Boolean, default=False)
    marked_numbers = db.Column(db.String(200), default='')  # Comma-separated marked numbers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Store called numbers and their call order
called_numbers = []
game_mode = "Classic"

# Configuration
NUM_MONITOR_BALLS = 3  # Change this to adjust how many balls are displayed in the monitor
TOTAL_BALLS = 75  # Change this to adjust the total number of balls in the game
GAME_MODES = ["Classic", "4 corners", "Speed", "Coverall"]
ADMIN_PASSWORD = "admin"  # Change this to a secure password

@app.route('/control')
def index():
    """Main page to mark called numbers"""
    return render_template('control.html', called=called_numbers, total_balls=TOTAL_BALLS)

@app.route('/monitor')
def monitor():
    """Separate page to show last N called balls"""
    return render_template('monitor.html', num_balls=NUM_MONITOR_BALLS, total_balls=TOTAL_BALLS)

@app.route('/api/call/<int:number>', methods=['POST'])
def call_number(number):
    """Mark a number as called"""
    if 1 <= number <= TOTAL_BALLS:
        if number not in called_numbers:
            called_numbers.append(number)
            return jsonify({
                'success': True,
                'message': f'Number {number} called',
                'called': called_numbers,
                'last_three': called_numbers[-NUM_MONITOR_BALLS:]
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Number {number} already called'
            }), 400
    return jsonify({'success': False, 'message': 'Invalid number'}), 400

@app.route('/api/undo', methods=['POST'])
def undo():
    """Remove the last called number"""
    if called_numbers:
        removed = called_numbers.pop()
        return jsonify({
            'success': True,
            'message': f'Removed number {removed}',
            'called': called_numbers,
            'last_three': called_numbers[-NUM_MONITOR_BALLS:]
        })
    return jsonify({'success': False, 'message': 'No numbers to undo'}), 400

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset all called numbers"""
    global called_numbers
    called_numbers = []
    return jsonify({'success': True, 'message': 'Game reset', 'called': called_numbers})

@app.route('/api/state')
def get_state():
    """Get current game state"""
    return jsonify({
        'called': called_numbers,
        'last_three': called_numbers[-NUM_MONITOR_BALLS:] if called_numbers else [],
        'game_mode': game_mode,
        'available_modes': GAME_MODES
    })

@app.route('/api/game-mode', methods=['GET'])
def get_game_mode():
    """Get current game mode"""
    return jsonify({
        'game_mode': game_mode,
        'available_modes': GAME_MODES
    })

@app.route('/api/game-mode/<mode>', methods=['POST'])
def set_game_mode(mode):
    """Set current game mode"""
    global game_mode
    if mode in GAME_MODES:
        game_mode = mode
        return jsonify({
            'success': True,
            'message': f'Game mode set to {mode}',
            'game_mode': game_mode
        })
    return jsonify({'success': False, 'message': 'Invalid game mode'}), 400

# Authentication Routes
@app.route('/')
def home():
    """Home page with login"""
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    data = request.get_json()
    password = data.get('password', '')
    
    if password == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid password'}), 401

@app.route('/logout')
def logout():
    """Handle logout"""
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/control')
def control():
    """Control page - requires admin access"""
    if not session.get('admin'):
        return redirect(url_for('home'))
    return render_template('control.html', called=called_numbers, total_balls=TOTAL_BALLS)

# Card Management Routes
@app.route('/register-card')
def register_card():
    """Card registration page"""
    return render_template('register_card.html')

@app.route('/api/register-card', methods=['POST'])
def api_register_card():
    """Register a new bingo card"""
    data = request.get_json()
    card_id = data.get('card_id', '').strip()
    player_name = data.get('player_name', '').strip()
    card_numbers = data.get('card_numbers', None)  # For paper card input
    
    if not card_id or not player_name:
        return jsonify({'success': False, 'message': 'Card ID and player name required'}), 400
    
    # Check if card already exists
    existing = BingoCard.query.filter_by(card_id=card_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Card ID already registered'}), 400
    
    # Use provided numbers or generate new ones
    if card_numbers and len(card_numbers) == 25:
        # Validate paper card numbers
        numbers_list = [int(n) for n in card_numbers]
    else:
        # Generate random bingo card (5x5 grid = 25 numbers)
        import random
        numbers_list = [0] * 25
        
        # Generate one number per row for each column
        for row in range(5):
            for col in range(5):
                if row == 2 and col == 2:  # Free space in center
                    numbers_list[row * 5 + col] = 0
                else:
                    # Get valid range for this column (BINGO ranges)
                    start = col * 15 + 1
                    end = start + 15
                    
                    # Find a valid number not yet used in this column
                    while True:
                        num = random.randint(start, end)
                        # Check if this number is already used in this column
                        col_numbers = [numbers_list[r * 5 + col] for r in range(5) if r != row]
                        if num not in col_numbers:
                            numbers_list[row * 5 + col] = num
                            break
    
    card = BingoCard(
        card_id=card_id,
        player_name=player_name,
        numbers=','.join(map(str, numbers_list))
    )
    
    db.session.add(card)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Card registered successfully',
        'card_id': card_id
    })

@app.route('/card/<card_id>')
def digital_card(card_id):
    """Display a digital bingo card"""
    card = BingoCard.query.filter_by(card_id=card_id).first()
    if not card:
        return render_template('card_not_found.html'), 404
    
    numbers = list(map(int, card.numbers.split(',')))
    marked = set(map(int, card.marked_numbers.split(','))) if card.marked_numbers else set()
    
    return render_template('digital_card.html', card=card, numbers=numbers, marked=marked, called=called_numbers)

@app.route('/api/mark-number', methods=['POST'])
def mark_number():
    """Mark a number on a card"""
    data = request.get_json()
    card_id = data.get('card_id')
    number = data.get('number')
    
    card = BingoCard.query.filter_by(card_id=card_id).first()
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    marked = set(map(int, card.marked_numbers.split(','))) if card.marked_numbers else set()
    
    if number == 0:  # Free space
        marked.add(0)
    else:
        marked.add(number)
    
    card.marked_numbers = ','.join(map(str, marked))
    
    # Check for bingo
    if check_bingo(card.numbers, card.marked_numbers):
        card.has_bingo = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'has_bingo': card.has_bingo,
        'marked': list(marked)
    })

def check_bingo(numbers_str, marked_str):
    """Check if marked numbers form a bingo pattern"""
    numbers = list(map(int, numbers_str.split(',')))
    marked = set(map(int, marked_str.split(',')))
    
    # Check rows
    for row in range(5):
        if all(numbers[row * 5 + col] in marked or numbers[row * 5 + col] == 0 for col in range(5)):
            return True
    
    # Check columns
    for col in range(5):
        if all(numbers[row * 5 + col] in marked or numbers[row * 5 + col] == 0 for row in range(5)):
            return True
    
    # Check diagonals
    if all(numbers[i * 5 + i] in marked or numbers[i * 5 + i] == 0 for i in range(5)):
        return True
    if all(numbers[i * 5 + (4 - i)] in marked or numbers[i * 5 + (4 - i)] == 0 for i in range(5)):
        return True
    
    return False

@app.route('/admin-cards')
def admin_cards():
    """Admin page to manage all cards"""
    if not session.get('admin'):
        return redirect(url_for('home'))
    
    cards = BingoCard.query.all()
    # Convert to dictionaries for JSON serialization
    cards_data = [{
        'id': card.id,
        'card_id': card.card_id,
        'player_name': card.player_name,
        'has_bingo': card.has_bingo,
        'round_number': card.round_number,
        'created_at': card.created_at.isoformat()
    } for card in cards]
    return render_template('admin_cards.html', cards=cards_data, called=called_numbers)

@app.route('/api/admin-check-bingo/<int:card_id>', methods=['POST'])
def admin_check_bingo(card_id):
    """Admin endpoint to check and mark bingo for a card"""
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    card = BingoCard.query.get(card_id)
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    # Auto-mark called numbers
    numbers = set(map(int, card.numbers.split(',')))
    marked = numbers & set(called_numbers)
    marked.add(0)  # Free space
    
    card.marked_numbers = ','.join(map(str, marked))
    
    if check_bingo(card.numbers, card.marked_numbers):
        card.has_bingo = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'has_bingo': card.has_bingo,
        'marked_numbers': list(marked)
    })

@app.route('/api/unmark-number', methods=['POST'])
def unmark_number():
    """Unmark a number on a card"""
    data = request.get_json()
    card_id = data.get('card_id')
    number = data.get('number')
    
    card = BingoCard.query.filter_by(card_id=card_id).first()
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    marked = set(map(int, card.marked_numbers.split(','))) if card.marked_numbers else set()
    
    if number in marked:
        marked.remove(number)
    
    card.marked_numbers = ','.join(map(str, marked))
    
    # Uncheck bingo status if unmarking
    if card.has_bingo:
        if not check_bingo(card.numbers, card.marked_numbers):
            card.has_bingo = False
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'has_bingo': card.has_bingo,
        'marked': list(marked)
    })

@app.route('/api/delete-card/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    """Delete a card"""
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    card = BingoCard.query.get(card_id)
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    card_info = {'card_id': card.card_id, 'player_name': card.player_name}
    db.session.delete(card)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Card {card_info["card_id"]} deleted successfully'
    })

@app.route('/api/update-card/<int:card_id>', methods=['POST'])
def update_card(card_id):
    """Update card player name or round number"""
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    card = BingoCard.query.get(card_id)
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    if 'player_name' in data:
        card.player_name = data['player_name'].strip()
    if 'round_number' in data:
        card.round_number = int(data['round_number'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Card updated successfully',
        'card': {
            'id': card.id,
            'card_id': card.card_id,
            'player_name': card.player_name,
            'round_number': card.round_number
        }
    })

@app.route('/admin-paper-cards')
def admin_paper_cards():
    """Admin page to check paper cards"""
    cards = BingoCard.query.all()
    # Convert to dictionaries for JSON serialization
    cards_data = [{
        'id': card.id,
        'card_id': card.card_id,
        'player_name': card.player_name,
        'numbers': list(map(int, card.numbers.split(','))),
        'has_bingo': card.has_bingo,
        'round_number': card.round_number,
        'created_at': card.created_at.isoformat()
    } for card in cards]
    return render_template('admin_paper_cards.html', cards=cards_data, called=called_numbers)

@app.route('/admin-add-paper-card')
def admin_add_paper_card():
    """Page to add a new paper card"""
    return render_template('admin_add_paper_card.html')

@app.route('/api/add-paper-card', methods=['POST'])
def api_add_paper_card():
    """Add a new paper card with specific numbers"""
    data = request.get_json()
    card_id = data.get('card_id', '').strip()
    player_name = data.get('player_name', '').strip()
    numbers = data.get('numbers', [])
    
    if not card_id or not player_name:
        return jsonify({'success': False, 'message': 'Card ID and player name required'}), 400
    
    if not isinstance(numbers, list) or len(numbers) != 25:
        return jsonify({'success': False, 'message': 'Must provide exactly 25 numbers'}), 400
    
    # Check if card_id already exists
    existing = BingoCard.query.filter_by(card_id=card_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Card ID already exists'}), 400
    
    # Validate numbers are integers
    try:
        numbers_list = [int(n) for n in numbers]
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'All numbers must be integers'}), 400
    
    card = BingoCard(
        card_id=card_id,
        player_name=player_name,
        numbers=','.join(map(str, numbers_list))
    )
    
    db.session.add(card)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Paper card added successfully',
        'card_id': card_id
    })

@app.route('/api/update-paper-card/<int:card_id>', methods=['POST'])
def api_update_paper_card(card_id):
    """Update a paper card"""
    if not session.get('admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    card = BingoCard.query.get(card_id)
    
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    if 'player_name' in data:
        card.player_name = data['player_name'].strip()
    
    if 'numbers' in data:
        numbers = data['numbers']
        if not isinstance(numbers, list) or len(numbers) != 25:
            return jsonify({'success': False, 'message': 'Must provide exactly 25 numbers'}), 400
        try:
            numbers_list = [int(n) for n in numbers]
            card.numbers = ','.join(map(str, numbers_list))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'All numbers must be integers'}), 400
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Paper card updated successfully'
    })

@app.route('/api/paper-card-status/<int:card_id>')
def get_paper_card_status(card_id):
    """Get marked numbers and bingo status for a paper card based on called numbers"""
    card = BingoCard.query.get(card_id)
    if not card:
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    
    # Get marked numbers based on called numbers
    card_numbers = set(map(int, card.numbers.split(',')))
    marked = card_numbers & set(called_numbers)
    marked.add(0)  # Always mark free space
    
    # Get card numbers as list
    numbers = list(map(int, card.numbers.split(',')))
    
    # Check for bingo
    has_bingo = check_bingo(card.numbers, ','.join(map(str, marked)))
    
    return jsonify({
        'success': True,
        'card_id': card.card_id,
        'player_name': card.player_name,
        'numbers': numbers,
        'marked': list(marked),
        'has_bingo': has_bingo
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0')
