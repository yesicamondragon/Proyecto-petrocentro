from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Post

class Form_post(forms.ModelForm):
    class Meta:
            model = Post
            fields = ['image','titulo', 'descripcion', 'categoria','estado' ,'empleado' ,'contenido' ]
            widgets = {
                'image': forms.ClearableFileInput(attrs={
                        'class': 'form-control',
                    }),
                        
                    'categoria': forms.Select(attrs={
                    'class': 'form-select',
                        
                    }),
                'titulo': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Título del post'
                }),
                'descripcion': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Breve descripción'
                }),
                'empleado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                }),
                'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                }),
                'contenido': SummernoteWidget(attrs={
                    'class': 'form-control',
                    'name': 'contenido'
                }),
            
            }
      # Personalización de los labels
    labels = {
        'titulo': 'Título del Post',  # Cambia el label de 'titulo'
        'descripcion': 'Descripción Breve',
        'categoria': 'Categoría',
        'empleado': '¿Este post es solo para los empleados?',  # Cambia el label de 'empleado'

        'contenido': 'Contenido del Post',
    }