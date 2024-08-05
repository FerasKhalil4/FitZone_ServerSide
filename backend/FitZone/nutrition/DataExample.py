from drf_spectacular.utils import OpenApiExample
plan_create = [
    OpenApiExample(
        name='example1',
        value={
            
	
	"name":"calorie deficit",
	"protein_required":200,
	"carbs_required":250,
	"fats_required":200,
	"calories_required":2500,
	"weeks_number":10,
	"notes":"lose weight",
	"is_same":False,
	"meals_schedule":[
		{
			"day":1,
			"meals_types":[
				{
					"type":"Breakfast",
					"meals":[
						{
							"name":"cake",
							"portion_size":1,
							"portion_unit":"spoon"
						},
							{
							"name":"milkshake",
							"portion_size":1,
							"portion_unit":"cup",
								"alternateives":{
									"1":"cake",
									"2":"potato"
								}
						}
					]
				}	,
						{
					"type":"Dinner",
					"meals":[
						{
							"name":"cake",
							"portion_size":1,
							"portion_unit":"spoon"
						},
							{
							"name":"milkshake",
							"portion_size":1,
							"portion_unit":"cup"
						}
					]
		}	
				
			]
		},
				{
			"day":2,
			"meals_types":[
				{
					"type":"Breakfast",
					"meals":[
						{
							"name":"cake",
							"portion_size":1,
							"portion_unit":"spoon"
						},
							{
							"name":"milkshake",
							"portion_size":1,
							"portion_unit":"cup",
								"alternateives":{
									"1":"cake",
									"2":"potato"
								}
						}
					]
				}	,
						{
					"type":"Dinner",
					"meals":[
						{
							"name":"cake",
							"portion_size":1,
							"portion_unit":"spoon"
						},
							{
							"name":"milkshake",
							"portion_size":1,
							"portion_unit":"cup"
						}
					]
		}	
				
			]
		},
						{
			"day":3,
					"same_as_day":2
			
		}
		
	]
	
	
	
	
        },
        description = 'make sure to add 7 meal schedules or just add one and turn is_same to True '
    )
]

meal = [
	OpenApiExample(
		name='example',
  value={
	
		"name":"milkshake chocolatae",
		"portion_size":1,
		"portion_unit":"cup",
			"alternateives":{
				"1":"chocloate"
			}
}
	)
]