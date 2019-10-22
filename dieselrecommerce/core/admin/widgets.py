from import_export.widgets import DecimalWidget


class RoundedDecimalWidget(DecimalWidget):
    def clean(self, value, row=None, *args, **kwargs):
        value = super().clean(value, row, *args, **kwargs)
        if value:
            value = round(value, 2)
        return value
