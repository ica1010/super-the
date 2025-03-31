from django import forms
from pos.models import  OrderItem
from pos.models  import Category, Product
from django import forms
from djmoney.forms.fields import MoneyField
from .models import Depense, Ingredient, Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','image', 'code', 'category']

 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout de classes Bootstrap pour le style
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom du produit'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['code'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Code produit'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})

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
        
        
        

# Formulaire pour l'ajout d'une dépense
class DepenseAddForm(forms.ModelForm):
    class Meta:
        model = Depense
        # On n'inclut pas le champ "date" (auto_now_add) et "delete" (pour la suppression)
        fields = ['name', 'note', 'justification', 'amount', 'in_cash']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'justification': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'in_cash': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formulaire pour la modification d'une dépense
class DepenseUpdateForm(forms.ModelForm):
    class Meta:
        model = Depense
        # Même champs que pour l'ajout ; la date ne se modifie pas et la suppression est gérée à part
        fields = ['name', 'note', 'justification', 'amount', 'in_cash']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'justification': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'in_cash': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formulaire pour confirmer la suppression d'une dépense
class DepenseDeleteForm(forms.ModelForm):
    confirm = forms.BooleanField(
        required=True,
        label="Confirmer la suppression",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Depense
        # Aucun champ du modèle n'est modifié ici ; seul le champ de confirmation est utilisé
        fields = []
