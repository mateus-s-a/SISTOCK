from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label="Data Inicial",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="Data Final",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    