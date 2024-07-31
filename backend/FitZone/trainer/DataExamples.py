from drf_spectacular.utils import OpenApiExample
approve_client = [
    OpenApiExample(
        name='example1',
        value={
	"registration_status":"accepted",
	"rejection_reason":None
},
    ),
      OpenApiExample(
        name='example2',
        value={
	"registration_status":"rejected",
	"rejection_reason":"no time available"
},
    )
]