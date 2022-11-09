from re import search
from django.forms import ModelForm, SelectDateWidget
from django import forms
from .models import ActiveAircraft
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Field
from crispy_forms.bootstrap import InlineField


class ActiveAircraft355(ModelForm):
    class Meta:
        model = ActiveAircraft
        fields = ['three55Code', 'Comments']



# MONTHS = {
#     1:_('jan'), 2:_('feb'), 3:_('mar'), 4:_('apr'),
#     5:_('may'), 6:_('jun'), 7:_('jul'), 8:_('aug'),
#     9:_('sep'), 10:_('oct'), 11:_('nov'), 12:_('dec')
# }

class Form355Filters(forms.Form):
    acftType = forms.ChoiceField(required=False, label='Acft Type', choices=())
    fromDate = forms.DateField(required=True, label='From')
    toDate = forms.DateField(required=True, label='To')
    search = forms.CharField(required=False)
    gotNailed = forms.BooleanField(required=False)
    callSign = forms.CharField(required=False)
    runway = forms.ChoiceField(required=False, choices=())


class Form355FiltersFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.form_method = 'post'
        # self.form_id = 'Form355FiltersForm'
        # self.form_class = 'navbar-nav justify-content-center'
        # self.form_method = 'post'
        self.label_class = 'nav-item'
        self.field_class = 'nav-item'
        # self.layout = Layout(
        #     Fieldset(
        #         'Filters',
        #         Field('acftType', css_class="nav-item") ,
        #         Field('fromDate', css_class="nav-item"),
        #         Field('toDate', css_class="nav-item"),
        #        HTML("""
        #     <p>RSU Crew Fields: <strong>below only applies to crew data</strong></p>
        #     """),
        #         Field('search', css_class="nav-item")
        #     ),
        #     Submit('submit', 'Submit', css_class="btn btn-light btn-outline-dark align-middle"),
        # )

        # self.add_input(Submit('submit', 'Submit', css_class="btn btn-light btn-outline-dark align-middle"))
        self.render_required_fields = True