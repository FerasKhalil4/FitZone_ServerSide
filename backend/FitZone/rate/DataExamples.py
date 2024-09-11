from drf_spectacular.utils import OpenApiExample

rate_create = [
    OpenApiExample(
        name = 'example',
        value={
	"value":2,
	"gym":4,
	"trainer":None,
	"is_app_rate":False
}
    ,
    description='send the item id when try to rate the branch or trainer, and send "is_app_rate" as True when rate the app'
    )
]