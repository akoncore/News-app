from rest_framework.serializers import(
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    ReadOnlyField,
    ValidationError
)
from .models import Comment
from apps.main.models import Post


class CommentSerializer(ModelSerializer):
    author_info = SerializerMethodField()
    replise_count = ReadOnlyField()
    is_reply = ReadOnlyField()
    
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'author_info', 'parent',
            'is_active','replise_count', 'is_reply',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['authoor','is_active']
        
    
    def get_author_info(self,obj):
        return {
            'id':obj.author.id,
            'username':obj.author.username,
            'full_name':obj.author.full_name,
            'avatar':obj.author.avatar.url if obj.author.avatar else None
        }
        

class CommentCreateSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'post','parent','content'
        ]
        
    
    def validate_post(self,value):
        if not Post.objects.filter(id = value.id).exists():
            raise ValidationError(
                'Post not found'
            )
        return value
    
    def validate_parent(self, value):
        if value:
            # Получаем пост из валидированных данных или из initial_data
            post_data = self.initial_data.get('post')
            if post_data:
                # Сравниваем ID поста родительского комментария с переданным ID поста
                if value.post.id != int(post_data):
                    raise ValidationError(
                        'Parent comment must belong to the same post.'
                    )
        return value
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    
class CommentUpdateSerializer(ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ['content']
        

class CommentDetailSerializer(CommentSerializer):
    replise = SerializerMethodField()
    
    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['replise']
        
    def get_replise(self,obj):
        if obj.parent is None:
            replise = obj.replise.filter(is_active = True).order_by('created_at')
            return CommentSerializer(replise,many=True,context = self.context).data
        return []