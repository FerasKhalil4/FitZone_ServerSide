from drf_spectacular.utils import OpenApiExample

private_purchasing = [
    OpenApiExample(
        name='example1',
        value={
	"products":[
		{
			
			"branch_product_id":75,
			"amount":2
			
		},
		{
			"branch_product_id":76,
			"amount":2
		},	
		{
			"branch_product_id":90,
			"amount":2
		}
	],

	"price_offers":[
		{
			"offer_id":8,
		"amount":2

		},
		{
			"offer_id":9,
		"amount":2

		}
		
	],
	"vouchers":[
		"ApSNgla84w"
	]
}
    )
]



public_purchasing = [
    OpenApiExample(
        name='example1',
        value={
	"products":[
		{
			
			"branch_product_id":75,
			"amount":4,
			"branch_id":1
			
		},
		{
			"branch_product_id":76,
			"amount":4,
			"branch_id":1
			
			
		},	
			{
			
			"branch_product_id":110,
			"amount":4,
			"branch_id":2
			
		}

	],


	"vouchers":[
		"ApSNgla84w"
	]
}
    )
]