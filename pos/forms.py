from django import forms
from pos.models import  OrderItem
from pos.models  import Category, Product
from django import forms
from djmoney.forms.fields import MoneyField
from .models import Ingredient, Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'size','image', 'code', 'category', 'price']

    price = MoneyField(
        decimal_places=0,
        max_digits=14,
        default_currency='XOF'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout de classes Bootstrap pour le style
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom du produit'})
        self.fields['size'].widget.attrs.update({'class': 'form-control', 'placeholder': 'taille'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['code'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Code produit'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prix'})

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            # Générer un code aléatoire si vide
            import uuid
            return str(uuid.uuid4())[:8]
        return code


                

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']
        # widgets = {
        #     'product_type': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_product_type'}),
        #     'category': forms.Select(attrs={'class': 'form-control select2-selection__rendered', 'id': 'id_category'}),
        #     'stock': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_stock'}),
        #     'alert_stock': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_alert_stock'}),
        # }

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ != 'CheckboxInput':
                field.widget.attrs.update({'class': 'form-control'})
                
 
class OrderItemUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["custom_product_name", "custom_product_price", "quantity"]
        
        
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'price', 'quantity', 'unit']
        price = MoneyField(
        decimal_places=0,
        max_digits=14,
        default_currency='XOF'
    )
        widget = {
        
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unité'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom'})
        self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prix'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Quantité'})
        self.fields['unit'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Unité'})  