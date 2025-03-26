from django.contrib import admin
from phonenumber_field.modelfields import PhoneNumberField
from unfold.admin import ModelAdmin
from .models import Client, Fournisseur, RemboursementClient, RemboursementFournisseur
from django import forms
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import SplitPhoneNumberField
# Define a custom form for the Fournisseur model
class ClientForm(forms.ModelForm):               
    # telephone = SplitPhoneNumberField() # Correctly instantiate the widget

    class Meta:
        model = Client
        
        fields =['nom', 'telephone', 'adresse', 'dette']  # Specify the fields you want to include in the form
    
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            # Ajouter une classe aux labels
            field.label_tag = lambda label: f'<label class="form-label">{label}</label>'
            # Ajouter des classes aux inputs
            field.widget.attrs.update({'class': 'form-control'})
            self.fields['telephone'].widget.attrs.update({'id': 'phone'})


class fournisseurForm(forms.ModelForm):               
    telephone = PhoneNumberPrefixWidget(widgets={}) # Correctly instantiate the widget

    class Meta:
        model = Fournisseur
        fields = ['logo', 'nom', 'telephone', 'adresse', 'dette']  # Specify the fields you want to include in the form
    
    def __init__(self, *args, **kwargs):
        super(fournisseurForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Ajouter une classe aux labels
            field.label_tag = lambda label: f'<label class="form-label">{label}</label>'
            # Ajouter des classes aux inputs
            field.widget.attrs.update({'class': 'form-control'})
            
class UpdateFournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['logo', 'nom', 'telephone', 'adresse', 'dette', 'ancienne_dette']

# Register the Fournisseur model with the custom admin interface
@admin.register(Fournisseur)
class ContactAdmin(ModelAdmin):
    form = fournisseurForm
    # Optionally customize the list display and other options
    list_display = ('nom', 'telephone',)  # Add more fields as needed
    search_fields = ('telephone',)  # Add search functionality if needed
    
@admin.register(Client)
class ClientAdmin(ModelAdmin):
    form = ClientForm
    list_display = ('nom', 'telephone',)  # Add more fields as needed
    search_fields = ('telephone',)  
    # Add search functionality if needed
    
@admin.register(RemboursementFournisseur)
class RemboursementFournisseurAdmin(ModelAdmin):
    list_display = ('fournisseur', 'montant','date')  # Add more fields as needed
    search_fields = ('fournisseur','date')  
    
    
@admin.register(RemboursementClient)
class RemboursementClientAdmin(ModelAdmin):
    list_display = ('client', 'montant','date')  # Add more fields as needed
    search_fields = ('client','date')  
    

