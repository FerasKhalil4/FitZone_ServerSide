from drf_spectacular.utils import OpenApiExample

diet_helper= [
    OpenApiExample(
        name='example 1 ',
        value={
            'age':12,
            'weight':100,
            'height':180,
            'bodyfat':20,
            'goal':'weight gain',
            'activity':1.3,
            'gender':'m'
        },
        description='goal: he can choose between weight gain or weight loss or healthy, gender: f or m\
            activity:Very Light = 1.3, Light= 1.55,Moderate = 1.65, Heavy = 1.8, Very Heavy = 2'
    )
]