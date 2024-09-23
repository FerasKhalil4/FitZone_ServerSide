from .models import * 
from django.db.models import Q

class BlockService():
    
    @staticmethod
    def get_query(data)-> Q:
        return Q(
                blocker=data['blocker'],
                blocked=data['blocked'],
            )
        
    @staticmethod
    def create_block(data)-> BlockList:
        
        try:
            
            query = BlockService.get_query(data)
            block_entry = BlockList.objects.get(query)
            
            if not block_entry.blocking_status :
                block_entry.blocking_status = True
                block_entry.save()
            return block_entry
        
        except BlockList.DoesNotExist:
            return BlockList.objects.create(**data)
