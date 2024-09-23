from .functions import recommend_by_calories
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import ast


def get_nutrtional_list(data) -> list:
    return[data['max_Calories'],data['max_daily_fat'],data['max_daily_Saturatedfat']
           ,data['max_daily_Cholesterol'],data['max_daily_Sodium'],data['max_daily_Carbohydrate'],
            data['max_daily_Fiber'],data['max_daily_Sugar'],data['max_daily_Protein']
    ]
    
    
def get_ingredients(recommended_data,index):
    
    ingredients_str = recommended_data.iloc[index]['RecipeIngredientParts']
    ingredients_str = ingredients_str.replace('c(', '[').replace(')', ']')
    try:
        return ast.literal_eval(ingredients_str)
    except (SyntaxError, ValueError) as e:
        return [] 
    
    
def get_sent_data(recommended_data):
    retrieved_data = []
    for index in range(len(recommended_data)):
        ingredients = get_ingredients(recommended_data, index)
        retrieved_data.append({
                    'name':recommended_data.iloc[index]['Name'],
                    'ingredients' : ingredients,
                    'calories':recommended_data.iloc[index]['Calories'],
                    'fats':recommended_data.iloc[index]['FatContent'],
                    'saturated_fat':recommended_data.iloc[index]['SaturatedFatContent'],
                    'sugar':recommended_data.iloc[index]['SugarContent'],
                    'protein':recommended_data.iloc[index]['ProteinContent'],
                    'carbohydrate':recommended_data.iloc[index]['CarbohydrateContent'],
                    'sodium':recommended_data.iloc[index]['SodiumContent'],
                    'cholesterol':recommended_data.iloc[index]['CholesterolContent'],
                })
    return retrieved_data
    
@api_view(['POST'])
def diet_helper(request,*args, **kwargs):
    try:
        max_daily_fat = request.data['max_nutritional_values']['max_daily_fat']
        data = request.data['max_nutritional_values']
        ingredient_filter = request.data.pop('ingredient_filter',None)

        ingredient_filter = [ingredient_filter[i].lower() for i in range(len(ingredient_filter))]
        
        max_nutritional_values = get_nutrtional_list(data)
        recommended_data = recommend_by_calories(max_daily_fat, max_nutritional_values,ingredient_filter)

        return Response({'data':get_sent_data(recommended_data)},status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)