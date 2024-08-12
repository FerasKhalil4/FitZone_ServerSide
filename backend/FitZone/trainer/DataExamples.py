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
group = [
    OpenApiExample(
        name='example1',
        value={
            "gym":1,
            "start_hour":"23:00:00",
            "session_length":90,
            "group_capacity":4,
            "days_off":{
            "1":"sunday",
            "2":"monday"

            }
}
    )
]