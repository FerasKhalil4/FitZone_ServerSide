from .functions import Weight_Gain ,Weight_Loss,Healthy
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Food
from .serializers import FoodSerializer
from .DateExamples import diet_helper
from .services import SaveMealsService
from wallet.models import Wallet , Wallet_Deposit
from user.models import Client
from nutrition.models import NutritionPlan
from nutrition.serializers import NutritionPlanSerializer
from drf_spectacular. utils import extend_schema


@extend_schema(
    summary='use the diet helper to get a diet plan',
    examples= diet_helper
    
)
@api_view(['POST'])

def index(request):
    try:
        client = Client.objects.get(user=request.user.pk)
        wallet = Wallet.objects.get(client=client)
        
        if wallet.balance < 100:
            return Response({'error': 'Balance must have at least 100 to use this service'},status=status.HTTP_400_BAD_REQUEST)
        
    except Client.DoesNotExist:
        return Response({'error':'client does not exist'},status=status.HTTP_400_BAD_REQUEST)
    
    age=int(request.POST.get("age"))
    weight=int(request.POST.get("weight"))
    height=int(request.POST.get("height"))
    bodyfat=float(request.POST.get("bodyfat"))
    goal=request.POST.get("goal")
    activity=float(request.POST.get("activity"))
    gender=request.POST.get("gender")
    

    leanfactor=0.0
    if(gender=="m"):
        if(10<=bodyfat<=14):
            leanfactor=1
        elif(15<=bodyfat<=20):
            leanfactor=0.95
        elif(21<=bodyfat<=28):
            leanfactor=0.90
        else:
            leanfactor=0.85    
    else:
        if(14<=bodyfat<=18):
            leanfactor=1
        elif(19<=bodyfat<=28):
            leanfactor=0.95
        elif(29<=bodyfat<=38):
            leanfactor=0.90
        else:
            leanfactor=0.85            


    maintaincalories=int(weight*24*leanfactor*activity)
    
    caloriesreq=0
    finaldata=[]
    bmi=0
    bmiinfo=""
    if(goal=="weight gain"):
        print("wg")
        finaldata=Weight_Gain(age,weight,height)
        bmi=int(finaldata[len(finaldata)-2])
        bmiinfo=finaldata[len(finaldata)-1]
        caloriesreq=maintaincalories+300
    if(goal=="weight loss"):
        print("wl")
        finaldata=Weight_Loss(age,weight,height)
        bmi=int(finaldata[len(finaldata)-2])
        bmiinfo=finaldata[len(finaldata)-1]
        caloriesreq=maintaincalories-300
    
    if(goal=="healthy"):
        print("h")
        finaldata=Healthy(age,weight,height)
        print(finaldata)
        bmi=int(finaldata[len(finaldata)-2])
        bmiinfo=finaldata[len(finaldata)-1]
        caloriesreq=maintaincalories

    breakfastdata=Food.objects.all().filter(bf=1).filter(name__in=finaldata)
    lunchdata=Food.objects.all().filter(lu=1).filter(name__in=finaldata)
    dinnerdata=Food.objects.all().filter(di=1).filter(name__in=finaldata)

    data = { 
        "message":"make sure to save the wanted meals before leaveing",
        "breakfast":FoodSerializer(breakfastdata,many=True).data,
        "lunch":FoodSerializer(lunchdata,many=True).data,
        "dinner":FoodSerializer(dinnerdata,many=True).data,
        "bmi":bmi,
        "bmiinfo":bmiinfo,
        "caloriesreq":caloriesreq
    }
    
    Wallet_Deposit.objects.create(
        client = client,
        amount = 100,
        tranasaction_type = 'cut'
    )
    
    wallet.balance -= 100
    wallet.save()
    
    return Response(data,status=status.HTTP_200_OK)
    
class ClientMealPlanListAV(generics.CreateAPIView):
    serializer_class = NutritionPlanSerializer
    queryset = NutritionPlan.objects.filter(is_active=True)
    
    def post(self, request, *args, **kwargs):
        try:
            request.data.update({	
                "name":"helper diet plan",
                "weeks_number":10,
                "notes":"helper diet plan",
                "is_same":True,
                })
            client = Client.objects.get(user = request.user.pk)

            return Response(SaveMealsService.save(request.data,client),status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    
client_diet = ClientMealPlanListAV.as_view()
    