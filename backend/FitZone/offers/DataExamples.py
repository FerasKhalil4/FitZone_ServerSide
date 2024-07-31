from drf_spectacular.utils import OpenApiExample

fee_percentage_creation = [
    OpenApiExample(
        name = 'example',
        value ={
            "start_date": "2024-8-10",
            "end_date": "2024-10-10",
            "offer_data": {
                "percentage_cut": 10,
                "fee": 1
            }
        }
    )
]
category_percentage_creation = [
    OpenApiExample
    (
        
       name =  'create offer for product category',
        value ={
        "start_date":"2024-8-10",
        "end_date":"2024-10-10",
        "offer_data":
        {	"percentage_cut":10,
        "category":1,
        "supp_category":0

        }
        }
        
    ),
        OpenApiExample
    (
       name =  'create offer for supplement category',
        
       value = {
        "start_date":"2024-8-10",
        "end_date":"2024-10-10",
        "offer_data":
            {
                "percentage_cut":10,
                "category":1,
                "supp_category":1

            }
        }
        
    )
]
class_offer_percetage = [
    OpenApiExample(
        name = 'example',
       value = {
	"start_date":"2024-8-10",
	"end_date":"2024-10-10",
	"offer_data":
	{	"percentage_cut":10,
	 "class_id":1	 
	}
}
    )
]

fee_price_offers = [
    OpenApiExample(
        name = 'example',
    value =    {
	"start_date":"2024-10-10",
	"end_date":"2024-10-30",
	"offer_data":
	{	"price":10,
	 "fee":1
	}
}
    )
]

prouduct_price_offers = [
    OpenApiExample(
        name = 'example',
        
       value = {
	"branch_id":1,
	"name":"offer_1",
	"start_date":"2024-8-10",
	"end_date":"2024-10-10",
	"offer_data":
	{	"price":10,
	 "objects_data":[
		 {
			 "product":5,
			 "number":1
		 },
		 {
			 "product":6,
			 "number":1
		 }		 
	 ]
	
	}
},
        description = 'the number is refers to the number of the products',
        
        
    )
]

update_percentage_offer = [
    OpenApiExample(
        name='update the offer related to the fee"',
        value={
            "start_date": "2024-8-10",
            "end_date": "2024-10-10",
            "offer_data": {
                "percentage_cut": 20,
                "fee": 1
            }
        },
    ),
    OpenApiExample(
        name='update the offer related to the class',
        value={
            "start_date": "2024-8-10",
            "end_date": "2024-10-10",
            "offer_data": {
                "percentage_cut": 20,
                "class_id": 1
            }
        },
    ),
    OpenApiExample(
        name='update the offer related to the category',
        value={
            "start_date": "2024-8-10",
            "end_date": "2024-10-10",
            "offer_data": {
                "percentage_cut": 20,
                "category": 1
            }
        },
    ),
    OpenApiExample(
        name='update the offer related to the supplement category',
        value={
            "start_date": "2024-8-10",
            "end_date": "2024-10-10",
            "offer_data": {
                "percentage_cut": 20,
                "category": 1,
                "supp_category": 1
            }
        },
    )
]

update_price_offers = [
    OpenApiExample
    (
        name = 'example',
        
      value =  {
	"start_date":"2024-10-10",
	"end_date":"2024-10-30",
	"offer_data":
	{	"price":30,
	 "objects_data":[
		 {
			 "product":3,
			 "number":1
		 },
		 {
			 "product":4,
			 "number":3
		 }		 
	 ]
	
	}
},
        description= 'update the price offer related to products'
    ),
    OpenApiExample(
        name = 'example2',
        
             value =   {
	"start_date":"2024-8-10",
	"end_date":"2024-10-10",
	"offer_data":
	{	"price":20,
	 "fee":1	 
	}
},
    description= 'update the price offer related to fee'
        
    )
    
]