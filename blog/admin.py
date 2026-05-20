from django.contrib import admin
from .models import Contactus,Post,Profile,Like,Comment,Follow

# Register your models here.

admin.site.register(Contactus)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)

