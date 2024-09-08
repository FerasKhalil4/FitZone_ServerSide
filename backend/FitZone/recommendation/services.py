from .models import Food
from nutrition.models import NutritionPlan, MealsSchedule, MealsType, Meals
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.core.exceptions import ValidationError

class SaveMealsService():
    
    @staticmethod
    def get_meals(meal_name,meal,current_cal,calories_req_per_meal,meal_instance) -> float:
        check_cal = 0
        
        for item in meal:
            food = Food.objects.get(pk=item['pk'])
            check_cal += food.cal * item['amount']
            
            Meals.objects.create(
                meals_type = meal_instance,
                name = food.name,
                portion_size = item['amount'],
                portion_unit = 'amount'
            )
            
        if ((calories_req_per_meal * 0.95)) < check_cal < ((calories_req_per_meal * 1.05)):
            return current_cal + check_cal
        else:
            print(check_cal)
            error = f'please check on the amount of the food you entered for the {meal_name} your required calories for this meal {calories_req_per_meal}'
            error += f' you need to add at least {abs((calories_req_per_meal * 0.95 ) - check_cal)}' if (calories_req_per_meal - check_cal) > 0 else \
            f' you need to cut on at least {abs((calories_req_per_meal * 1.05) - check_cal)}'
            error += f' your current calories for this meal {check_cal}'
            raise ValueError(error)
        
    @staticmethod
    def check_active_plans(client, now) -> None:
        check = NutritionPlan.objects.filter(client=client,start_date__lte = now, end_date__gte = now , is_active=True)
        print(check)
        if check.exists():
            raise ValidationError({'error': 'this client already has an active plan'})
        
    @staticmethod
    def save(data, client) -> NutritionPlan:
        try:
            with transaction.atomic():
                
                calories_req = data.pop('calories')
                current_cal = 0
                name = data.pop('name')
                weeks_number = data.pop('weeks_number')
                notes = data.pop('notes')
                is_same = data.pop('is_same')
                now = datetime.now().date()
                
                calorie_intake_per_meal = {
                    'Breakfast': calories_req * 0.3,
                    'Lunch':calories_req * 0.4,
                    'Dinner':calories_req * 0.3,
                    'buffer_range': calories_req * 1.05,
                    'minimum_range': calories_req * 0.95
                }
                SaveMealsService.check_active_plans(client, now)
                end_date = now + relativedelta(weeks=weeks_number)
                
                nutrition_plan = NutritionPlan.objects.create(
                    name=name,
                    weeks_number=weeks_number,
                    notes=notes,
                    is_same=is_same,
                    client=client,
                    start_date = now,
                    end_date = end_date
                )
                schedule = MealsSchedule.objects.create(
                    nutrition_plan = nutrition_plan,
                    day = 1
                )
                
                for meal_name,item in data.items():
                    meal = MealsType.objects.create(
                        meals_schedule=schedule,
                        type = meal_name,
                    )
                    current_cal = SaveMealsService.get_meals(meal_name,item,current_cal,calorie_intake_per_meal[meal_name],meal)
                return {'message':'Nutrition Plan Created Successfully'}                
                
        except Exception as e:
            raise ValueError(str(e))
            

        
            