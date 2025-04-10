import os
import sys
import json
import torch
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Optional, Union

class MealPlanGenerator:
    """A class to generate personalized meal plans using a language model."""
    
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", cache_dir: Optional[str] = None):
        """
        Initialize the meal plan generator with a specified language model.
        
        Args:
            model_name: The name or path of the model to use
            cache_dir: Optional directory to cache the downloaded model
        """
        self.model_name = model_name
        print(f"🔄 Loading model {model_name}...")
        
        # Model initialization with error handling
        try:
            model_kwargs = {"torch_dtype": torch.float16, "low_cpu_mem_usage": True}
            if cache_dir:
                model_kwargs["cache_dir"] = cache_dir
                
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
            self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
            
            # Device selection with fallback options
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                print("✅ Using GPU acceleration (CUDA)")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = torch.device("mps")
                print("✅ Using Apple Silicon acceleration (MPS)")
            else:
                self.device = torch.device("cpu")
                print("⚠️ Using CPU (GPU not available)")
                
            self.model = self.model.to(self.device)
            
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise
            
        # Load cuisine guidelines from external file if available
        self.cuisine_guidelines = self._load_cuisine_guidelines()
        
    def _load_cuisine_guidelines(self) -> Dict[str, Dict[str, str]]:
        """Load cuisine guidelines from a JSON file if available, otherwise use defaults."""
        try:
            if os.path.exists("cuisine_guidelines.json"):
                with open("cuisine_guidelines.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load cuisine guidelines: {str(e)}")
            
        # Default guidelines if file not available
        return {
            "indian": {
                "non-vegetarian": """
                - Include tandoori preparations for lean proteins
                - Balance meat dishes with vegetable sides
                - Use yogurt-based marinades for protein tenderizing
                - Incorporate fish curries from coastal regions
                """,
                "vegetarian": """
                - Focus on protein-rich lentil dishes (various dals)
                - Include paneer and tofu preparations
                - Use dairy products for protein boost
                - Incorporate high-protein grains like quinoa adapted to Indian flavors
                """,
                "vegan": """
                - Emphasize legume variety (chickpeas, lentils, beans)
                - Include tofu and tempeh with Indian spices
                - Use coconut milk instead of dairy
                - Focus on protein-rich grain combinations
                """
            },
            "mediterranean": {
                "non-vegetarian": """
                - Prioritize fish and seafood 2-3 times weekly
                - Include poultry and eggs in moderate amounts
                - Limit red meat to occasional consumption
                - Use olive oil as primary fat source
                """,
                "vegetarian": """
                - Emphasize legumes daily (chickpeas, lentils, beans)
                - Include variety of nuts and seeds
                - Use eggs and dairy as protein sources
                - Incorporate whole grains in every meal
                """,
                "vegan": """
                - Create protein-complete meals with legume-grain combinations
                - Use tahini and nut butters for richness
                - Incorporate seitan and tempeh with Mediterranean herbs
                - Focus on bean-based dishes and dips
                """
            },
            "asian": {
                "non-vegetarian": """
                - Balance proteins with vegetables in stir-fries
                - Include fish and seafood regularly
                - Use small amounts of meat for flavoring
                - Incorporate eggs in various preparations
                """,
                "vegetarian": """
                - Use tofu, tempeh and edamame as protein staples
                - Incorporate eggs in noodle and rice dishes
                - Include dairy in Indian-Asian fusion dishes
                - Use mushrooms for umami flavor
                """,
                "vegan": """
                - Feature tofu and tempeh in main dishes
                - Use seitan for meat-like texture
                - Include variety of mushrooms for depth
                - Emphasize fermented foods like kimchi
                """
            }
        }

    def get_cuisine_guidelines(self, cuisine_style: str, dietary_preference: str) -> str:
        """
        Get specific guidelines for a cuisine and dietary preference.
        
        Args:
            cuisine_style: The style of cuisine (e.g., "indian", "mediterranean")
            dietary_preference: Dietary preference (e.g., "vegetarian", "non-vegetarian")
            
        Returns:
            String containing guidelines or default text if not found
        """
        return self.cuisine_guidelines.get(cuisine_style.lower(), {}).get(
            dietary_preference.lower(), 
            "Default guidelines - adapt recipes to meet nutritional requirements for the specified goal."
        )

    def format_prompt(self, prompt: str) -> str:
        """
        Format a prompt for the language model.
        
        Args:
            prompt: The raw prompt to format
            
        Returns:
            Formatted prompt ready for the model
        """
        return f"<|system|>You are a professional nutritionist and chef. Your goal is to create detailed, healthy, and practical meal plans.</s><|user|>{prompt}</s><|assistant|>"

    def generate_text(self, prompt: str, max_tokens: int = 2048, 
                     temperature: float = 0.8, top_p: float = 0.95) -> str:
        """
        Generate text using the language model.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (lower is more deterministic)
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text response
        """
        formatted_prompt = self.format_prompt(prompt)
        
        try:
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt", 
                                   padding=True, truncation=True, max_length=2048)
            input_length = inputs['input_ids'].shape[1]
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Calculate available token space
            max_new_tokens = min(1500, 2048 - input_length)
            
            # Generation with progress indicator
            print(f"🔄 Generating content (max {max_new_tokens} new tokens)...")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=100,
                    repetition_penalty=1.3,
                    no_repeat_ngram_size=3,
                    num_beams=5,
                    length_penalty=1.2,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_tokens = outputs[0][input_length:]
            return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
        except Exception as e:
            print(f"❌ Error during text generation: {str(e)}")
            raise

    def save_meal_plan_to_file(self, meal_plan: str, filename: Optional[str] = None, 
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save the generated meal plan to a file.
        
        Args:
            meal_plan: The generated meal plan text
            filename: Optional custom filename, otherwise auto-generated
            metadata: Optional metadata to include in the saved file
            
        Returns:
            Path to the saved file
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = "meal_plans"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                goal = metadata.get("goal", "custom").lower().replace(" ", "_") if metadata else "plan"
                cuisine = metadata.get("cuisine_style", "").lower() if metadata else ""
                filename = f"{output_dir}/meal_plan_{cuisine}_{goal}_{timestamp}.md"
            elif not os.path.dirname(filename):
                # If only filename provided without path, put in output directory
                filename = f"{output_dir}/{filename}"
                
            # Add markdown frontmatter with metadata if available
            final_content = meal_plan
            if metadata:
                frontmatter = "---\n"
                for k, v in metadata.items():
                    if isinstance(v, list):
                        frontmatter += f"{k}: [{', '.join(v)}]\n"
                    else:
                        frontmatter += f"{k}: {v}\n"
                frontmatter += "---\n\n"
                final_content = frontmatter + meal_plan
            
            with open(filename, "w", encoding="utf-8") as file:
                file.write(final_content)
                
            print(f"✅ Meal plan saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save meal plan: {str(e)}")
            fallback_filename = "meal_plan_emergency_backup.txt"
            try:
                with open(fallback_filename, "w", encoding="utf-8") as file:
                    file.write(meal_plan)
                print(f"⚠️ Emergency backup saved to {fallback_filename}")
                return fallback_filename
            except:
                print("❌ Could not save backup file either")
                return None

    def generate_meal_plan(self, 
                          goal: str = "muscle gain",
                          days: int = 3, 
                          dietary_preference: str = "non-vegetarian",
                          cuisine_style: str = "indian", 
                          allergies: Optional[List[str]] = None,
                          calories: Union[str, int] = "2500-3000",
                          max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Generate a complete customized meal plan.
        
        Args:
            goal: Nutritional goal (e.g., "muscle gain", "weight loss")
            days: Number of days in the meal plan
            dietary_preference: Dietary preference (e.g., "vegetarian")
            cuisine_style: Preferred cuisine style
            allergies: List of allergies or dietary restrictions
            calories: Target calorie range (either string range or specific int)
            max_tokens: Maximum tokens for generation
            
        Returns:
            Dictionary with status, meal plan, and metadata
        """
        if allergies is None:
            allergies = []
            
        # Validate inputs
        days = max(1, min(14, days))  # Limit days to reasonable range
        
        # Format calorie information
        calorie_info = f"between {calories} kcal" if isinstance(calories, str) else f"approximately {calories} kcal"
        
        # Base prompt with more context
        base_prompt = f"""You are a Certified Nutritionist & Chef specializing in {cuisine_style.title()} cuisine 
with expertise in {dietary_preference} diets. Design a detailed and practical meal plan optimized 
for {goal}, featuring authentic {cuisine_style.title()} recipes adapted for {dietary_preference} requirements.

The meal plan should be realistic and implementable with readily available ingredients while maintaining 
cultural authenticity. Balance nutrition with practicality and taste.
"""

        # Dietary requirements
        dietary_requirements = f"""
### Dietary Specifications
- **Primary Goal**: {goal.title()}
- **Diet Type**: {dietary_preference.title()}
- **Cuisine Style**: {cuisine_style.title()}
- **Daily Calories**: Ensure total daily calories are {calorie_info}
- **Allergies/Restrictions**: {', '.join(allergies) if allergies else 'None'}

### Cuisine-Specific Guidelines
{self.get_cuisine_guidelines(cuisine_style, dietary_preference)}
"""

        # Day meal structure template
        day_meal_structure = """
### Detailed Meal Plan for Day {day}

Provide the following meals with complete details:

1. **Breakfast** (Morning Energy Boost)
   - Main dish with protein source
   - Side items and beverages
   - Timing: Early morning meal
   
2. **Mid-Morning Snack**
   - Light, nutritious options
   - Protein or fruit-based choices
   
3. **Lunch** (Mid-day Fuel)
   - Complete main course
   - Side dishes and accompaniments
   - Recommended beverages
   
4. **Evening Snack**
   - Energy-sustaining options
   - Small but satisfying portions
   
5. **Dinner** (Evening Nourishment)
   - Full main course
   - Balanced side dishes
   - Light beverage options

For each meal, include:
1. 🍽️ **Recipe Name & Description**
2. ⚖️ **Exact Portions & Measurements**
3. 📊 **Complete Nutritional Breakdown**
   - Calories: exact kcal
   - Protein: g
   - Carbs: g
   - Fats: g
   - Fiber: g
4. 🥘 **Ingredients List**
5. 👩‍🍳 **Preparation Steps** (step-by-step with precise cooking times and techniques)
6. ⌚ **Timing Guidelines**
7. 💡 **Tips & Substitutions**
"""

        try:
            print(f"🔄 Generating {days}-day meal plan for {goal} with {cuisine_style} {dietary_preference} cuisine...")
            meal_plan_text = f"# {days}-Day {cuisine_style.title()} {dietary_preference.title()} Meal Plan for {goal.title()}\n\n"
            meal_plan_text += f"*Generated on {datetime.now().strftime('%B %d, %Y')}*\n\n"
            meal_plan_text += "## Overview\n\n"
            meal_plan_text += f"This meal plan is designed for {goal} with {cuisine_style.title()} cuisine adapted for a {dietary_preference} diet.\n\n"
            
            if allergies:
                meal_plan_text += f"**Allergies/Restrictions:** {', '.join(allergies)}\n\n"
                
            meal_plan_text += f"**Target Daily Calories:** {calorie_info}\n\n"
            meal_plan_text += "---\n\n"

            # Generate each day's plan
            for day in range(1, days + 1):
                print(f"🔄 Generating Day {day}/{days}...")
                day_prompt = f"{base_prompt}\n{dietary_requirements}\n{day_meal_structure.format(day=day)}"
                day_text = self.generate_text(day_prompt, max_tokens)
                meal_plan_text += f"## Day {day}\n\n{day_text}\n\n---\n\n"

            # Generate general sections with more specific guidance
            print("🔄 Generating additional sections...")
            general_sections_prompt = f"""{base_prompt}
{dietary_requirements}

Provide the following practical guidance sections for the entire {days}-day meal plan:

1. **Weekly Shopping List**
   - Organize by food category (produce, proteins, pantry items, etc.)
   - Include exact quantities needed for the full plan
   - Note shelf-stable vs fresh items
   - Suggest budget-friendly alternatives

2. **Meal Prep Strategy**
   - Provide a detailed weekly meal prep timeline
   - Identify which components can be prepared in advance
   - Include storage instructions and shelf life information
   - Batch cooking recommendations

3. **Portion Control & Scaling**
   - Guidelines for adjusting portions based on individual needs
   - How to scale recipes up or down
   - Visual portion size references

4. **Progress Tracking & Adjustments**
   - Signs that the meal plan is working for the stated goal
   - Common issues and how to troubleshoot them
   - When and how to make adjustments
"""
            general_sections_text = self.generate_text(general_sections_prompt, max_tokens)
            meal_plan_text += "## Additional Guidance\n\n" + general_sections_text

            # Save and return
            metadata = {
                "goal": goal,
                "days": days,
                "dietary_preference": dietary_preference,
                "cuisine_style": cuisine_style,
                "calories": calories,
                "allergies": allergies,
                "generation_date": datetime.now().strftime("%Y-%m-%d"),
                "model": self.model_name
            }
            
            filename = self.save_meal_plan_to_file(meal_plan_text, metadata=metadata)
            
            return {
                "status": "success",
                "meal_plan": meal_plan_text,
                "file_path": filename,
                "metadata": metadata
            }
            
        except Exception as e:
            error_msg = f"An error occurred during meal plan generation: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "metadata": {
                    "goal": goal,
                    "days": days,
                    "dietary_preference": dietary_preference,
                    "cuisine_style": cuisine_style,
                    "allergies": allergies
                }
            }


# Command-line interface setup
def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate detailed meal plans using AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--model", type=str, default="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                        help="Language model to use for generation")
    parser.add_argument("--goal", type=str, default="muscle gain",
                        help="Nutritional goal (e.g., weight loss, maintenance, muscle gain)")
    parser.add_argument("--days", type=int, default=3,
                        help="Number of days in the meal plan (1-14)")
    parser.add_argument("--diet", type=str, default="non-vegetarian",
                        help="Dietary preference (e.g., vegetarian, vegan, non-vegetarian)")
    parser.add_argument("--cuisine", type=str, default="indian",
                        help="Cuisine style (e.g., indian, mediterranean, asian)")
    parser.add_argument("--allergies", type=str, nargs="+", default=[],
                        help="List of allergies or foods to avoid")
    parser.add_argument("--calories", type=str, default="2500-3000",
                        help="Target calorie range (e.g., '2000-2500' or specific value)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output filename (optional)")
    parser.add_argument("--cache-dir", type=str, default=None,
                        help="Directory to cache the downloaded model")
    
    # Use parse_known_args to handle additional args from Jupyter/Colab
    return parser.parse_known_args()


# Run the script with flexibility for different environments
if __name__ == "__main__":
    try:
        # Handle both direct command line usage and Jupyter/Colab execution
        if any(notebook_env in sys.modules for notebook_env in ['ipykernel', 'google.colab', 'colab']):
            print("🔍 Detected Jupyter/Colab environment")
            print("To generate a meal plan, create a MealPlanGenerator instance:")
            print("\nExample:")
            print("------------------")
            print("generator = MealPlanGenerator()")
            print("result = generator.generate_meal_plan(")
            print("    goal='weight loss',")
            print("    days=5,")
            print("    dietary_preference='vegetarian',")
            print("    cuisine_style='mediterranean'")
            print(")")
            # Don't do anything else - let the user import and use the class
        else:
            # Command line usage
            args, unknown = parse_args()
            if unknown:
                print(f"⚠️ Ignoring unknown arguments: {unknown}")
            
            # Create the meal plan generator
            generator = MealPlanGenerator(model_name=args.model, cache_dir=args.cache_dir)
            
            # Generate the meal plan
            result = generator.generate_meal_plan(
                goal=args.goal,
                days=args.days,
                dietary_preference=args.diet,
                cuisine_style=args.cuisine,
                allergies=args.allergies,
                calories=args.calories
            )
            
            if result["status"] == "success":
                print("\n✅ Meal plan generation complete!")
                print(f"📄 Saved to: {result['file_path']}")
                
                # Print a preview
                preview_lines = result["meal_plan"].split("\n")[:20]
                print("\n=== Preview ===\n")
                print("\n".join(preview_lines))
                print("\n...(content continues)...\n")
            else:
                print(f"\n❌ Failed to generate meal plan: {result.get('error', 'Unknown error')}")
                
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")