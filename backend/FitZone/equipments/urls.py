from django.urls import path
from .views import *
urlpatterns = [
    path('equipment/',Equipment_lisAtV , name='equipementsListAV'),
    path('equipment/<int:pk>/',Equipment_detailAV,name='equipment_detail'),
    path('<int:branch_id>/',diagram_listAV,name='diagrams_list'),
    path('<int:diagram_id>/<int:branch_id>/',diagram_detailsAV, name = 'diagram_detail'),
    path('exercises/',excerciseList,name = 'exercises_list'),
    path('exercises-gym/<int:branch_id>/',equipment_excerciseList,name = 'equipment_excercise_list'),
    path('equipment-create/<int:diagram_id>/',diagramEquipmentsCreate,name = 'diagramEquipmentsCreate'),
    
]
