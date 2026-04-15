# card/forms.py
from django import forms
from .models import Stamp

class StampForm(forms.ModelForm):
    class Meta:
        model = Stamp
        # ユーザーに入力させる項目（author は自動入力なのでここには書かない）
        fields = ['name', 'description', 'world', 'x', 'y', 'z', 'radius', 'is_hidden']
        
        # HTMLの入力枠にBootstrapのクラス（デザイン）を割り当てる
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'world': forms.Select(attrs={'class': 'form-control'}),
            'x': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'X'}),
            'y': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Y'}),
            'z': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Z'}),
            'radius': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_hidden': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }