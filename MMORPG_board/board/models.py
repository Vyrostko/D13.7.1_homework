from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    TANKS = 'Танки'
    HEALTH = 'Хилы'
    DD = 'ДД'
    MERCHANTS = 'Торговцы'
    GILDMASTERS = 'Гилдмастеры'
    QUESTGIVERS = 'Квестгиверы'
    BLACKSMITHS = 'Кузнецы'
    LEATHERWORKERS = 'Кожевники'
    POTIONS = 'Зельевары'
    SPELLMASTERS = 'Мастера заклинаний'
    CATEGORY_CHOICES = (
        (TANKS, 'Танки'),
        (HEALTH, 'Хилы'),
        (DD, 'ДД'),
        (MERCHANTS, 'Торговцы'),
        (GILDMASTERS, 'Гилдмастеры'),
        (QUESTGIVERS, 'Квестгиверы'),
        (BLACKSMITHS, 'Кузнецы'),
        (LEATHERWORKERS, 'Кожевники'),
        (POTIONS, 'Зельевары'),
        (SPELLMASTERS, 'Мастера заклинаний'),
    )
    categoryType = models.TextField(choices=CATEGORY_CHOICES, default=MERCHANTS)

    def __str__(self):
        return f"{self.categoryType}"

class Comment(models.Model):
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    commentAuthor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.commentAuthor}"

    def get_absolute_url(self):
        return f'/ads/'

class Ad(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    text = models.TextField()
    image = models.ImageField(upload_to='images_uploaded', blank=True, null=True)
    video = models.FileField(upload_to='videos_uploaded', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    file = models.FileField(upload_to='files_uploaded', blank=True, null=True)
    adCategory = models.ForeignKey(Category, on_delete=models.CASCADE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(Comment, related_name='ads_comments')

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return f'/ads/ad/{self.id}'