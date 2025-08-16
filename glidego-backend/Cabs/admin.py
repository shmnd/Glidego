from django.contrib import admin
from .models import CabAdmin,Cab,Driver,Vehicle
# Register your models here.
admin.site.register(CabAdmin)
admin.site.register(Cab)
admin.site.register(Vehicle)
admin.site.register(Driver)

