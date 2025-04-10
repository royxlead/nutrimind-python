from flask import Flask, request, jsonify
from flask_cors import CORS
from model.meal_planner import MealPlanGenerator

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the Flask app
CORS(app)

# Initialize MealPlanGenerator instance
generator = MealPlanGenerator()

@app.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    """
    Endpoint to generate a meal plan based on user input.
    Expects a JSON payload with the following fields:
    - goal: Nutritional goal (e.g., "muscle gain")
    - days: Number of days in the meal plan
    - dietary_preference: Dietary preference (e.g., "vegetarian")
    - cuisine_style: Preferred cuisine style (e.g., "indian")
    - allergies: List of allergies or dietary restrictions (optional)
    - calories: Target calorie range (optional)
    """
    try:
        # Parse input JSON
        data = request.get_json()
        goal = data.get('goal', 'muscle gain')
        days = data.get('days', 3)
        dietary_preference = data.get('dietary_preference', 'non-vegetarian')
        cuisine_style = data.get('cuisine_style', 'indian')
        allergies = data.get('allergies', [])
        calories = data.get('calories', '2500-3000')

        # Generate meal plan
        result = generator.generate_meal_plan(
            goal=goal,
            days=days,
            dietary_preference=dietary_preference,
            cuisine_style=cuisine_style,
            allergies=allergies,
            calories=calories
        )

        # Return result as JSON
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'meal_plan': result['meal_plan'],
                'file_path': result['file_path'],
                'metadata': result['metadata']
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Failed to generate meal plan')
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)