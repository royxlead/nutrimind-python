from meal_planner import MealPlanGenerator

generator = MealPlanGenerator()
result = generator.generate_meal_plan(
    goal="weight loss",
    days=5,
    dietary_preference="vegetarian",
    cuisine_style="mediterranean"
)

# Display the result
from IPython.display import Markdown
display(Markdown(result["meal_plan"]))