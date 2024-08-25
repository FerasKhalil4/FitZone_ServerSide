from django.db.models.signals import post_save ,post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product,Branch_products

@receiver(post_save,sender=Product)
@receiver(post_delete,sender=Product)
@receiver(post_save,sender=Branch_products)

def invalidate_cache(sender,instance,**kwargs):
    print(instance)
    print(sender)
    public_cache_key = 'public_store_products'
    cache.delete(public_cache_key)
    if isinstance(instance,Branch_products):
        gym = instance.branch.gym.pk
        private_cache_key = f'private_store_products{gym}'
        print(private_cache_key)
        cache.delete(private_cache_key)
        