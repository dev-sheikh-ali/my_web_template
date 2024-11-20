from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, class_name):
    """ Add a custom CSS class to form fields """
    if not field:
        return field
    # Get the current field's widget and add the class
    field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' ' + class_name
    return field
