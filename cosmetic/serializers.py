from rest_framework import serializers
from .models import *

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(required=False)
    product_kor_name = serializers.SerializerMethodField()
    product_eng_name = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    color_code = serializers.SerializerMethodField()
    product_url = serializers.SerializerMethodField()
    product_key = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
        'id', 'brand', 'product_category','category', 'product_kor_name', 'product_eng_name', 'product_image',
                'color_code','texture',  'product_url','product_key')

    def get_product_kor_name(self, obj):
        return obj.kor_name

    def get_product_eng_name(self, obj):
        return obj.eng_name

    def get_product_category(self, obj):
        return obj.category.id

    def get_category(self, obj):
        return obj.category.name

    def get_product_image(self, obj):
         request = self.context['request']
         try:
             return request.build_absolute_uri(obj.image.url)
         except:
             return None

    def get_product_key(self, obj):
        return obj.key

    def get_color_code(self, obj):
        return obj.color_code

    def get_product_url(self, obj):
        return obj.url