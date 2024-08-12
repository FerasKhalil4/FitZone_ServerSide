from drf_spectacular.utils import OpenApiExample

registration = [
    OpenApiExample(
        name='example1',
        value = {
   
		"user_profile": {
					"username": "usaaaaaer89",
					"email": "ssa@example.com",
					"password": "user",
					"password2": "user",
			    "gender":0,
					"birth_date": "2000-05-15"
			},
		"wakeup_time": "07:00",
		"address": "123 Main St",
	  "height":170.5,
	"goal":{
		"weight":120,
		"goal":"Lose Weight",
		"goal_weight":100,
		"predicted_date":"2025-01-01",
  'activity_level':'Low',
	},
	"diseases":[
		1,4
	]
} ,
        description ='where the diseases is an array of the diseases ids and it might be empty []'
    )
]