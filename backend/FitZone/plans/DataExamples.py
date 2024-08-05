from drf_spectacular.utils import OpenApiExample 
create_training_plan = [
    OpenApiExample(
            'Example 1',
            summary='Custom example 1',
            description='This is the first custom example , make sure to add 7 items in the workouts',
            value={
	"notes":"note_1",
	"plan_duration_weeks":6,
	"workouts":[
		{
			"name":"backday",
			"order":1,
			"is_rest":False,
			"has_cardio":False,
			"cardio_duration":None,
			"exercises":[
				{"exercise":95,
				 "sets":2,
				 "reps":{
					 "1":12,
					 "2": 10
				 },
				 "rest_time_seconds":120,
				 "order":1				 
				},			{"exercise":96,
				 "sets":2,
				 "reps":{
					 "1":12,
					 "2": 10
				 },
				 "rest_time_seconds":120,
				 "order":2
				}
				
			]
			
		} ,
		{
			"order":2,
			"is_rest":True,
			"has_cardio":False,
			"cardio_duration":None
		},
		{"order":3,
			"same_as_order":1

		}
		
	]
	
	
	
}

        ),
    ]
update_the_training_plan = [
        OpenApiExample
        (
        name = 'Example',
            value={
            "notes":"notes",
            "plan_duration_weeks":12
            }
        )
    ]

Exercise_to_workout_plan = [
        OpenApiExample
        (
        name = 'Example',
            value={"exercise":95,
                    "sets":2,
                    "reps":{
                        "1":12,
                        "2": 10
                    },
                    "rest_time_seconds":120,
                    "order":1				 
                    }
        )
    ]
update_workout = [
    OpenApiExample(
        'example 1',
        value=[    
                {
                    
                    "name":"pull day",
                            "order": 3,
                            "is_rest": False,
                            "has_cardio": True,
                            "cardio_duration": 39
                    
                }
        ]
    ),
    OpenApiExample(
        name = 'example 2',        
        value=
                {
                    
                    "name":"Rest",
                            "order": 2,
                            "is_rest": True,
                            "has_cardio": False,
                            "cardio_duration": None
                    
                }
    )
]

update_the_status = [
    OpenApiExample(
        name='example1',
        value={
            "is_active": False,
        }

    )
]
