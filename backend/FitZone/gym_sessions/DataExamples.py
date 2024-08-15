from drf_spectacular.utils import OpenApiExample

subscription = [
    OpenApiExample(
        name='example1',
        value={

	"registration_type":1,
	"offer_code":"12jdoksa",
	"vouchers":[
		"ApSNgla84w",
		"TSgT3UsDOZl"
	]

},
        description='where the registration_type is the registration_fee id of the branchs gym and \
            you can send the code of the percentage offer and vouchers code to use it ',
        
    )
]