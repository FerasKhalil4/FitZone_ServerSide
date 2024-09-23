from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services  import AdminStatsService, ManagerStatsService


@api_view(['GET'])
def admin_user_stats(request, *args, **kwargs):
    month = int(request.GET.get('month')) if 'month' in request.GET else None
    year_num = int(request.GET.get('year')) if 'year' in request.GET else None
    
    data = AdminStatsService.get_user_stats(month,year_num)
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_gym_stats(request, *args, **kwargs):    
    data = AdminStatsService.get_gym_stats()
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_vouchers_stats(request, *args, **kwargs):   
    month = int(request.GET.get('month')) if 'month' in request.GET else None
    year_num = int(request.GET.get('year')) if 'year' in request.GET else None 
    data = AdminStatsService.get_vouchers_data(month,year_num)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def manager_branches_stats(request, *args, **kwargs):   
    manager = request.user
    year_num = int(request.GET.get('year')) if 'year' in request.GET else None 
    data = ManagerStatsService.get_branches_stats(manager,year_num)
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_branches_activity_stats(request, *args, **kwargs):   
    manager = request.user
    year_num = int(request.GET.get('year')) if 'year' in request.GET else None 
    month = int(request.GET.get('month')) if 'month' in request.GET else None
    
    data = ManagerStatsService.get_branch_sessions_statistics(manager,year_num,month)
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_products_stats(request, *args, **kwargs):   
    manager = request.user
    year_num = int(request.GET.get('year')) if 'year' in request.GET else None 
    data = ManagerStatsService.get_products_sattistics(manager,year_num)
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_classes_stats(request, *args, **kwargs):   
    manager = request.user
    data = ManagerStatsService.get_classes_statistics(manager)
    return Response(data, status=status.HTTP_200_OK)
