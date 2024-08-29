from django import forms
from django.contrib.auth.models import User
from paginaPetrocentro.models import Usuario

class RegisterForm(forms.Form):
    
    identificacion = forms.IntegerField(required=True, widget=forms.TextInput(attrs={
        'id': 'identificacion',
        'name': 'identificacion',
        'class': 'form-control',
    }))
    telefono = forms.IntegerField(required=True, widget=forms.TextInput(attrs={
        'id': 'telefono',
        'name': 'telefono',
        'class': 'form-control',
        
    }))
    username = forms.CharField(min_length=4, required=True, widget=forms.TextInput(attrs={
        'id': 'username',
        'name': 'username',
        'class': 'form-control',
        
    }))
    nombre_completo = forms.CharField(min_length=4, required=True, widget=forms.TextInput(attrs={
        'id': 'first_name',
        'name': 'first_name',
        'class': 'form-control',
        
    }))
   
    correo_electronico = forms.EmailField(min_length=4, required=True, widget=forms.EmailInput(attrs={
        'id': 'email',
        'name': 'email',
        'class': 'form-control',
        
    }))
    contraseña = forms.CharField(min_length=4, required=True, widget=forms.PasswordInput(attrs={
        'id': 'password',
        'name': 'password',
        'class': 'form-control',
        
    }))
    confirmar_contraseña = forms.CharField(min_length=4, required=True, widget=forms.PasswordInput(attrs={
        'id': 'password2',
        'name': 'password2',
        'class': 'form-control',
        
    }))

    def save(self):
        return User.objects.create_user(
            self.cleaned_data.get('username'),
            self.cleaned_data.get('correo_electronico'),
            self.cleaned_data.get('contraseña'),
        )
    
 