from django import forms
import re
from .models import Estudiante, Asignatura


class BaseBootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()


class EstudianteForm(BaseBootstrapModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'matricula', 'carrera', 'correo']


class AsignaturaForm(BaseBootstrapModelForm):
    class Meta:
        model = Asignatura
        fields = ['codigo', 'nombre', 'creditos', 'profesor']


class ConsultaNotasForm(forms.Form):
    matricula = forms.CharField(label='Matrícula', max_length=20)
    clave = forms.CharField(label='Contraseña', widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        matricula = cleaned.get('matricula')
        clave = cleaned.get('clave')
        
        if matricula and clave:
            try:
                estudiante = Estudiante.objects.get(matricula=matricula)
            except Estudiante.DoesNotExist:
                raise forms.ValidationError(
                    'No existe un estudiante con esa matrícula. Verifica que la matrícula sea correcta.'
                )
            
            if not estudiante.clave:
                raise forms.ValidationError(
                    'Este estudiante no tiene contraseña asignada. Contacta al administrador.'
                )
            
            if not estudiante.check_clave(clave):
                raise forms.ValidationError(
                    'Contraseña incorrecta. Si olvidaste tu contraseña, contacta al administrador.'
                )
            
            cleaned['estudiante'] = estudiante
        
        return cleaned


class CambiarClaveForm(forms.Form):
    actual = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput())
    nueva1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput())
    nueva2 = forms.CharField(label='Confirmar nueva contraseña', widget=forms.PasswordInput())

    def __init__(self, estudiante: Estudiante, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.estudiante = estudiante

    def clean_actual(self):
        actual = self.cleaned_data.get('actual')
        if actual and not self.estudiante.check_clave(actual):
            raise forms.ValidationError('La contraseña actual no es válida.')
        return actual

    def clean_nueva1(self):
        nueva1 = self.cleaned_data.get('nueva1')
        if nueva1:
            if len(nueva1) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
            # Validación opcional: mayúsculas y números (comentado para no ser muy restrictivo)
            # if not re.search(r'[A-Z]', nueva1):
            #     raise forms.ValidationError('La contraseña debe contener al menos una mayúscula.')
            # if not re.search(r'[0-9]', nueva1):
            #     raise forms.ValidationError('La contraseña debe contener al menos un número.')
        return nueva1

    def clean(self):
        cleaned = super().clean()
        nueva1 = cleaned.get('nueva1')
        nueva2 = cleaned.get('nueva2')
        
        if nueva1 and nueva2 and nueva1 != nueva2:
            raise forms.ValidationError('Las contraseñas nuevas no coinciden.')
        
        return cleaned


