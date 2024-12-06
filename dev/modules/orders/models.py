from django.db import models
from .enums import *
from django.core.exceptions import MultipleObjectsReturned
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from core.uauth.models import User

class Object(models.Model):
    #evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    #title = models.CharField(max_length=45)
    object_type = models.CharField(choices=OBJECT_TYPE_CHOICES, max_length=45)

    #def __str__(self):
    #    return '{0} - {1}'.format(self.object_type,
    #                              Evaluation.get_address(self.evaluation))

    @classmethod
    def save_meta(cls, obj, key, value):
        object_meta, created = ObjectMeta.objects.get_or_create(
            ev_object=obj, meta_key=key)
        object_meta.meta_value = value
        object_meta.save()

    @classmethod
    def get_meta(cls, obj, key):
        
        try:
            return ObjectMeta.objects.values_list('meta_value', flat=True).get(ev_object=obj, meta_key=key)
        except (MultipleObjectsReturned, ObjectMeta.DoesNotExist):
            return ''
    
    @property
    def has_additional_buildings(self):
        return ObjectMeta.objects.filter(ev_object=self, meta_key__startswith='garage_').exists() or \
               ObjectMeta.objects.filter(ev_object=self, meta_key__startswith='shed_').exists() or \
               ObjectMeta.objects.filter(ev_object=self, meta_key__startswith='gazebo_').exists()

    @property
    def security(self):
        return Object.get_meta(self, 'security')

    @property
    def energy_efficiency(self):
        return Object.get_meta(self, 'energy_efficiency')

    @property
    def air_conditioning(self):
        return Object.get_meta(self, 'air_conditioning')

    @property
    def outside_deco(self):
        return Object.get_meta(self, 'outside_deco')

    @property
    def wastewater(self):
        return Object.get_meta(self, 'wastewater')

    @property
    def municipality(self):
        return Object.get_meta(self, 'municipality')

    @property
    def street(self):
        return Object.get_meta(self, 'street')

    @property
    def house_no(self):
        return Object.get_meta(self, 'house_no')

    @property
    def flat_no(self):
        return Object.get_meta(self, 'flat no')

    @property
    def build_years(self):
        return Object.get_meta(self, 'build_years')
        
    @property
    def renovation_years(self):
        return Object.get_meta(self, 'renovation_years')

    @property
    def room_count(self):
        return Object.get_meta(self, 'room_count')

    @property
    def living_size(self):
        return Object.get_meta(self, 'living_size')

    @property
    def land_size(self):
        return Object.get_meta(self, 'land_size')
    
    @property
    def land_purpose(self):
        return Object.get_meta(self, 'land_purpose')

    @property
    def building_floor_count(self):
        return Object.get_meta(self, 'building_floor_count')
    
    @property
    def apartament_floor(self):
        return Object.get_meta(self, 'apartament_floor')

    @property
    def floor_count(self):
        return Object.get_meta(self, 'floor_count')

    @property
    def foundation(self):
        return Object.get_meta(self, 'foundation')

    @property
    def walls(self):
        return Object.get_meta(self, 'walls')

    @property
    def inside_walls(self):
        return Object.get_meta(self, 'inside_walls')

    @property
    def subfloor(self):
        return Object.get_meta(self, 'subfloor')

    @property
    def roof(self):
        return Object.get_meta(self, 'roof')

    @property
    def windows(self):
        return Object.get_meta(self, 'windows')

    @property
    def inside_doors(self):
        return Object.get_meta(self, 'inside_doors')

    @property
    def outside_doors(self):
        return Object.get_meta(self, 'outside_doors')

    @property
    def parking_spaces(self):
        return Object.get_meta(self, 'parking_spaces')

    @property
    def basement(self):
        return Object.get_meta(self, 'basement')

    @property
    def balcony(self):
        return Object.get_meta(self, 'balcony')

    @property
    def interior_deco(self):
        return Object.get_meta(self, 'interior_deco')

    @property
    def interior_floors(self):
        return Object.get_meta(self, 'interior_floors')

    @property
    def ceiling_deco(self):
        return Object.get_meta(self, 'ceiling_deco')

    @property
    def electricity(self):
        return Object.get_meta(self, 'electricity')

    @property
    def gas(self):
        return Object.get_meta(self, 'gas')

    @property
    def heating(self):
        return Object.get_meta(self, 'heating')

    @property
    def water(self):
        return Object.get_meta(self, 'water')

    @property
    def garage_size(self):
        return Object.get_meta(self, 'garage_size')
    
    @property
    def garage_attached(self):
        return Object.get_meta(self, 'garage_attached')

    @property
    def garage_cars_count(self):
        return Object.get_meta(self, 'garage_cars_count')
    
    @property
    def shed_electricity(self):
        return Object.get_meta(self, 'shed_electricity')
    
    @property
    def shed_size(self):
        return Object.get_meta(self, 'shed_size')
    
    @property
    def shed_type(self):
        return Object.get_meta(self, 'shed_type')
    
    @property
    def gazebo_electricity(self):
        return Object.get_meta(self, 'gazebo_electricity')
    
    @property
    def gazebo_size(self):
        return Object.get_meta(self, 'gazebo_size')
    
    @property
    def gazebo_type(self):
        return Object.get_meta(self, 'gazebo_type')

    @property
    def obj_type(self):
        return Object.get_meta(self, 'object_type')


class ObjectMeta(models.Model):
    # object_meta_id = models.AutoField(primary_key=True, editable=False)
    ev_object = models.ForeignKey(Object, on_delete=models.CASCADE)
    meta_key = models.CharField(max_length=255)
    meta_value = models.CharField(max_length=255)

    def __str__(self):
        return self.meta_key


class ObjectImage(models.Model):
    object = models.ForeignKey(Object, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='object_images/')
    comment = models.CharField(max_length=255, blank=True)
    category = models.CharField(choices=IMAGE_CHOICES, max_length=45)
    uploaded_at = models.DateTimeField(auto_now_add=True)



class ImageAnnotation(models.Model):
    image = models.ForeignKey(ObjectImage, related_name='annotations', on_delete=models.CASCADE)
    x_coordinate = models.FloatField()
    y_coordinate = models.FloatField()
    annotation_text = models.TextField(blank=True)
    annotation_image = models.ImageField(upload_to='annotation_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_client')
    agency = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    evaluator = models.ForeignKey(User, related_name='evaluator_orders', on_delete=models.SET_NULL, null=True, blank=True)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(choices=STATUS_CHOICES, max_length=45)
    #priority = models.CharField(choices=PRIORITY_CHOICES, max_length=45)

    class Meta:
        permissions = [
            ('evaluate_order', 'Can evaluate order'),
            ('view_evaluator_orders', 'Can view evaluator orders'),
        ]

    @classmethod
    def redirect_landing(cls, self, session):
        #if 'selected_obj_type' not in session:
        #    return HttpResponseRedirect(reverse_lazy('auth:landing'))
        return self.render_to_response(self.get_context_data())
    
    def __str__(self):
        return f"Order {self.id} - {self.object.street} {self.object.house_no}, {self.object.municipality}"