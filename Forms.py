from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, RadioField
from wtforms.fields import EmailField


class CreateThread(Form):
    thread_username = StringField('Username:', [validators.Length(min=1, max=50), validators.DataRequired()])
    thread_title = StringField('Thread Title:', [validators.Length(min=1, max=150), validators.DataRequired()])
    thread_message = TextAreaField('Thread Message:', [validators.DataRequired()], render_kw={"rows": 10})
    thread_reply = TextAreaField('Reply By CarOrSell Staff:', render_kw={"rows": 5})


class CreateAnnouncement(Form):
    thread_username = StringField('Username:', [validators.Length(min=1, max=50), validators.DataRequired()])
    thread_title = StringField('Announcement Title:', [validators.Length(min=1, max=150), validators.DataRequired()])
    thread_message = TextAreaField('Announcement Message:', [validators.DataRequired()])
    thread_reply = TextAreaField('Reply By CarOrSell Staff:')
    announcement_type = StringField('Announcement Type:', [validators.Length(min=1, max=50), validators.DataRequired()])
    severity_level = StringField('Severity Level:', [validators.Length(min=1, max=50), validators.DataRequired()])


class CreateUserForm(Form):
    full_name = StringField('Full Name:', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('M', 'Male'), ('F', 'Female')], default='')
    email = EmailField('Email:', [validators.Email(), validators.DataRequired()])
    mobile_no = StringField('Mobile Number (+65):', [validators.Length(min=8, max=8), validators.DataRequired()])
    address = StringField('Address:', [validators.DataRequired()])
    postal_code = StringField('Postal Code:', [validators.Length(min=6, max=6), validators.DataRequired()])
    username = StringField('Username:', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password:', [validators.Length(min=1, max=50), validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password:', [validators.Length(min=1, max=50), validators.DataRequired()])
    member = SelectField('Membership:', [validators.DataRequired()], choices=[('Member', 'Member')])


class CreateAdminForm(Form):
    full_name = StringField('Name:', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('M', 'Male'), ('F', 'Female')], default='')
    email = EmailField('Email:', [validators.Email(), validators.DataRequired()])
    mobile_no = StringField('Mobile Number (+65):', [validators.Length(min=8, max=8), validators.DataRequired()])
    username = StringField('Username:', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password:', [validators.Length(min=1, max=50), validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password:', [validators.Length(min=1, max=50), validators.DataRequired()])
    member = SelectField('Membership:', [validators.DataRequired()], choices=[('', 'Select'), ('Member', 'Member'), ('Admin', 'Admin')], default='')


class LoginForm(Form):
    username = StringField('Username:', [validators.Length(min=1, max=50), validators.DataRequired()])
    password = PasswordField('Password:', [validators.Length(min=1, max=50), validators.DataRequired()])


class CreateSellCarForm(Form):
    car_model = StringField('Car Model:', [validators.Length(min=1, max=150), validators.DataRequired()])
    car_brand = SelectField('Car Brand:', [validators.DataRequired()], choices=[('', 'Select'), ('Audi', 'Audi'), ('BMW', 'BMW'), ('Tesla', 'Tesla')], default='')
    car_price = StringField('Your Selling Price (in S$):', [validators.Length(min=1, max=150), validators.DataRequired()])
    condition = SelectField('Car Condition:', [validators.DataRequired()], choices=[('', 'Select'), ('Good', 'Good'), ('Fair', 'Fair'), ("Used", "Used")], default='')
    remarks = TextAreaField('Remarks:', [validators.Optional()], render_kw={"rows": 5})


class CreateOrderForm(Form):
    address = StringField('Address:', [validators.Length(min=1, max=200), validators.DataRequired()])
    postal_code = StringField('Postal Code:', [validators.Length(min=6, max=6), validators.DataRequired()])
    card_name = StringField('Name on Card:', [validators.Length(min=1, max=200), validators.DataRequired()])
    card_no = StringField('Card Number:', [validators.Length(min=16, max=16), validators.DataRequired()])
    expmonth = StringField('Card Expiry Month (MM):', [validators.Length(min=2, max=2), validators.DataRequired()])
    expyear = StringField('Card Expiry Year (YY):', [validators.Length(min=2, max=2), validators.DataRequired()])
    cvv = StringField('CVV:', [validators.Length(min=3, max=3), validators.DataRequired()])

class CreateCarsForm(Form):
    car_model = StringField('Car Model', [validators.Length(min=1, max=150), validators.DataRequired()])
    car_brand = SelectField('Car Brand', choices=[('', 'Select'), ('Audi', 'Audi'), ('BMW', 'BMW'), ('Tesla', 'Tesla')], default='')
    car_price = StringField('Car price (SGD___,___)', [validators.Length(min=1, max=150), validators.DataRequired()])
