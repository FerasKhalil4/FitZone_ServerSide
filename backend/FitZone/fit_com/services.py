from .models import Saved_Posts, Comments_Replies
from community.models import *
from user.models import Client
from django.db.models import Q
from trainer.models import Client_Trainer
from datetime import datetime
from community.models import Comments,Reactions
from gym_sessions.models import Gym_Subscription


class PostService():
    
    @staticmethod
    def get_client_posts(user) -> Post:
        
        posts = []
        now = datetime.now().date()
        
        try:
            client = Client.objects.get(user = user.pk)
        except Client.DoesNotExist:
            raise ValueError('Client does not exist')
        
        
        gyms = Gym_Subscription.objects.filter(
            client = client,
            start_date__lte = now,
            end_date__gte = now,
            is_active = True
            
        )
        gym_ids = []
        for item in gyms:
            if item.branch.gym.pk not in gym_ids:
                gym_ids.append(item.branch.gym.pk )
        print(gym_ids)
                
        query = Q(
            gym__pk__in = gym_ids  
        ) | Q (
            gym__allow_public_posts=True
        )
        print(Gym.objects.get(pk=2).allow_public_posts)
        
        try:
            trainer = Client_Trainer.objects.get(client=client,start_date__lte = now, end_date__gte= now, registration_status = 'accepted',is_deleted=False).trainer.employee
            query |= Q(
                poster = trainer
            ) | Q(
                poster__trainer__allow_public_posts = True
            )
            
        except Client_Trainer.DoesNotExist:
            pass
            
        query &= Q(
            is_approved = True
        )
        posts = Post.objects.filter(query).order_by('created_at')

        return posts        
        
class PostIntercationsService():
    
    @staticmethod
    def handle_comments(post,comment,client):
        post.comments_count += 1
        post.save()
        return Comments.objects.create(
            post = post,
            client = client,
            comment = comment
        ).comment
        
        
    @staticmethod
    def handle_reaction(post,reaction,client):
        try:
            check = Reactions.objects.get(client=client,post=post)
            check.reaction = reaction
            check.save()
            
            return reaction
        
        except Reactions.DoesNotExist:
            post.reaction_count += 1
            post.save()
            
            return Reactions.objects.create(
                post = post,
                client = client,
                reaction = reaction
            ).reaction
    @staticmethod
    def handle_delete_comment(post,comment,client):
        try:
            comment = Comments.objects.get(pk=comment,post=post.pk,is_deleted=False)
        except Comments.DoesNotExist:
            return {'message':'comment does not exist'}
        if comment.client == client:
            comment.is_deleted = True
            comment.save()

            replies = Comments_Replies.objects.filter(comment=comment)
            replies.update(is_deleted=True)
            replies_count = replies.count()
            post.comments_count -= (replies_count + 1)
            post.save()
            return {'message':'comment is deleted successfully'}
                
    @staticmethod
    def save_post(post,client):
        check = Saved_Posts.objects.filter(client=client, post=post, unsaved = False)
        if check.exists():
            return {'message':'post is already saved'}
        Saved_Posts.objects.create(
            post = post,
            client = client
        )
        return {'message':'post is saved successfully'}
    
    @staticmethod
    def handle_reply(post,comment,reply,client):
        post.comments_count += 1
        post.save()
        
        try:
            comment = Comments.objects.get(pk = comment,is_deleted=False)
        except Comments.DoesNotExist:
            return {'message':'Comment not found'}
        return Comments_Replies.objects.create(
            client = client, 
            comment = comment,
            reply=reply
        ).reply
    
    @staticmethod
    def handle_deleted_reply(post,comment):

        try:
            comment = Comments_Replies.objects.get(pk=comment,is_deleted=False)
        except Comments.DoesNotExist:
            return {'message':'reply not found'}
        
        comment.is_deleted = True
        comment.save()
        
        post.comments_count -= 1
        post.save()
        
        return {'message':'reply deleted successfully'}
    
    @staticmethod
    def unsave_post(post,client):
        try:
            post = Saved_Posts.objects.get(client=client,post=post)
        except Saved_Posts.DoesNotExist:
            return {'message':'post does not exist in you savings'}
        post.delete()
        return {'message':'post was unsaved successfully'}