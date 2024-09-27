from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()

class SelectColumnForm(forms.Form):
    y_axis = forms.ChoiceField(choices=[])
    
class GraphTypeForm(forms.Form):
    GRAPH_CHOICES = [
        ('monthly_yearly_mean', 'Monthly Yearly Mean (Y-axis required)'),
        ('Yearly_mean_for_temp', 'Yearly Mean for Temperature'),
        ('Yearly_mean_for_max_daily_temp', 'Yearly Mean for Max Daily Temperature'),
        ('daily_max_temp', 'Daily Max Temperature'),
        ('wind_rose', 'Wind Rose Graph')
    ]
    graph_type = forms.ChoiceField(choices=GRAPH_CHOICES, widget=forms.RadioSelect)
