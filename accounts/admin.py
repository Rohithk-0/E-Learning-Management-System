
from django.contrib import admin
from .models import User
from .models import Country, State, District

# Register your models here.
admin.site.register(User)

admin.site.register(Country)
admin.site.register(State)
admin.site.register(District)