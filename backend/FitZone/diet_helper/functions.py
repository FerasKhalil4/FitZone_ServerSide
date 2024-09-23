from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from FitZone.settings import BASE_DIR
import os


data=pd.read_csv(os.path.join(BASE_DIR ,"static/recipes.csv"))

dataset=data.copy()
columns=['RecipeId','Name','CookTime','PrepTime','TotalTime','RecipeIngredientParts','Calories','FatContent','SaturatedFatContent',
         'CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent','RecipeInstructions']

dataset=dataset[columns]

class RecommendationEngine():
    
    def scaling(self,dataframe):
        
        scaler=StandardScaler()
        prep_data=scaler.fit_transform(dataframe.iloc[:,6:15].to_numpy())
        return prep_data,scaler
    
    

    def nn_predictor(self,prep_data):

        neigh = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10)
        neigh.fit(prep_data)
        return neigh



    def build_pipeline(self,neigh,scaler,params):

        transformer = FunctionTransformer(neigh.kneighbors,kw_args=params)
        pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])
        return pipeline



    def extract_data(self,dataframe,ingredient_filter,max_nutritional_values):
        
        extracted_data=dataframe.copy()
        
        for column,maximum in zip(extracted_data.columns[6:15],max_nutritional_values):
            extracted_data=extracted_data[extracted_data[column]<maximum]
        
        if ingredient_filter!=None:
            print('in filtering the ingredients')
            for ingredient in ingredient_filter:
                extracted_data=extracted_data[extracted_data['RecipeIngredientParts'].str.contains(ingredient,regex=False)] 
                
        return extracted_data



    def apply_pipeline(self,pipeline,_input,extracted_data):
        return extracted_data.iloc[pipeline.transform(_input)[0]]



    def recommand(self,dataframe,_input,max_nutritional_values,ingredient_filter=None,params={'return_distance':False}):
        
        extracted_data=self.extract_data(dataframe,ingredient_filter,max_nutritional_values)
        prep_data,scaler=self.scaling(extracted_data)
        neigh=self.nn_predictor(prep_data)
        pipeline=self.build_pipeline(neigh,scaler,params)
        
        return self.apply_pipeline(pipeline,_input,extracted_data)


def recommend_by_calories(max_daily_fat, max_nutritional_values, ingredient_filter=None, params={'return_distance':False}):
    
    engine = RecommendationEngine()
    # Extract data based on maximum nutritional values and ingredient filter
    extracted_data = engine.extract_data(dataset, ingredient_filter, max_nutritional_values)
    
    # Scale the data
    prep_data, scaler = engine.scaling(extracted_data)
    
    # Fit the Nearest Neighbors model
    neigh = engine.nn_predictor(prep_data)
    
    # Build the pipeline
    pipeline = engine.build_pipeline(neigh, scaler, params)
    
    # Create a test input with specified calories
    test_input = np.array([[0] * 9])  # Assuming the input shape is (1, 9) for 9 nutritional features
    test_input[0, 1] = max_daily_fat  # Set the calories
    
    # Get recipe recommendation based on test input
    recommended_recipe = engine.apply_pipeline(pipeline, test_input, extracted_data)
    
    return recommended_recipe
