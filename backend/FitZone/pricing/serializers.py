from rest_framework import serializers
from gym.models import Branch, Gym
from .services import update_classes_registration_pricings, update_branch_products_pricings, update_gym_pricings, transaction

class PricingSerializer(serializers.Serializer):
    percentage = serializers.FloatField(write_only=True)
    type_of_pricing = serializers.CharField(write_only=True)



class GymSubscriptionPricingSerailizer(PricingSerializer,serializers.ModelSerializer):

    class Meta:
        model = Gym
        fields = ['percentage','type_of_pricing']
    
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                validated_data['gym'] = instance
                update_gym_pricings(validated_data)
                return {'message':'success'}
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        
class BranchProductsPricingSerailizer(PricingSerializer,serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ['percentage','type_of_pricing']
    
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                validated_data['branch'] = instance
                update_branch_products_pricings(validated_data)
                return {'message':'success'}
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        
        
class ClassRegistrationPricingSerailizer(PricingSerializer,serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ['percentage','type_of_pricing']
    
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                validated_data['branch'] = instance
                update_classes_registration_pricings(validated_data)
                return {'message':'success'}
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        
                

        
        