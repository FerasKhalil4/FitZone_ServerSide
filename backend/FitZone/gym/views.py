from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView 
from rest_framework import generics
from .seriailizers import GymSerializer 
from .models import Gym

# class Gym