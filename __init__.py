from flask import Flask, render_template, request, redirect, url_for, flash, session
from MyAes import encrypt, decrypt, get_fixed_key
from User import User
from Forms import CreateThread, CreateUserForm, CreateAdminForm, CreateSellCarForm, LoginForm, CreateOrderForm, CreateAnnouncement, CreateCarsForm, SearchBar
import shelve, User, Thread, sellcar, Order, Announcement, Cars, bcrypt, re
from flask_login import login_user, login_required, logout_user, LoginManager
from email_validator import validate_email, EmailNotValidError

admin = __import__("admin")

app = Flask(__name__)
app.secret_key = 'ff59a421971cd4de00539f85d307e6bb'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # If user is not logged in

@login_manager.user_loader
def load_user(id):
    db = shelve.open('database/users.db', 'r')
    db_content = db['Users']
    if db_content.get(id) is None:
        return None
    else:
        return db_content.get(id)


# Clear Session On Run START
@app.before_first_request
def before_first_request():
    logout_user()
    session['logged_in'] = False
    session['logged_in_admin'] = False
# Clear Session On Run END


# Session Error/Exploit Prevention START
@app.route('/authentication-required')
def authentication_required():
    return render_template('authentication-required.html')


@app.route('/admin-authentication-required')
def admin_authentication_required():
    return render_template('admin-authentication-required.html')
# Session Error/Exploit Prevention END

@app.errorhandler(405)
def method_not_allowed(e):
    print(e)
    app.logger.error(f"error: {e}, route: {request.url}")
    return render_template('error405.html'), 405

# Error 404 Handling START
@app.errorhandler(404)
def page_not_found(e):
    print(e)
    app.logger.error(f"error: {e}, route: {request.url}")
    return render_template('error404.html',), 404
# Error 404 Handling END 

@app.route('/about_me')
def about():
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('authentication-required.html')
    else:
        try:
            users_dict = {}
            db = shelve.open('database/users.db', 'r')
            users_dict = db['Users']
            db.close()

            users_list = []
            if session.get('user_id') is not None:
                users_list.append(users_dict.get(session.get('user_id')))

            return render_template('about_me.html', count=len(users_list), users_list=users_list)
        except:
            print("Error1")


# Landing Page START
@app.route('/')
def home():
    return render_template('home.html')
# Landing Page END

# Login/Logout Function START
@app.route('/login', methods=['GET', 'POST'])
def login():
    if (session['logged_in'] == False) or (session['logged_in_admin'] == False):
        login_form = LoginForm(request.form)
        if request.method == "POST" and login_form.validate():
            username = login_form.username.data            
            password = login_form.password.data
            db = shelve.open('database/users.db', 'r')
            db_content = db['Users']
            username_list = []
            regex = r'[^A-Za-z0-9]+'         
            if (re.findall(regex, username) != [] and re.findall(regex, password) != []) or (re.findall(regex, username) != [] or re.findall(regex, password) != []):
                print("Special characters found in login input page!")
                flash("Incorrect username or password!", category='error')
                flash("No special special characters allowed in input fields!", category='error')
                return render_template('login.html', form=login_form)
            for key in db_content:
                content = db_content[key]
                print(content.get_username())
                username_list.append(content.get_username())
                print(list(set(username_list)))
            if username not in username_list:
                print("Username not found in database!")
                flash("Username not registered!", category='error')
                return render_template('login.html', form=login_form)
            else: 
                print("Username exist")
                # this compares the digest of the password (when register for account) with the digest of the
                # password input
                if bcrypt.checkpw(password.encode(), content.get_password()):
                    print("digest matches!")
                    flash('You have logged in successfully.', category='success')
                    login_user(content, remember=True)
                    session['user_id'] = content.get_user_id()
                    if content.get_member() == 'Admin':
                        session['logged_in_admin'] = True
                        return redirect(url_for('admin_dashboard'))
                    else:
                        session['logged_in'] = True
                        return redirect(url_for('home'))
                else:
                    print("password digests don't match")
                    flash('Incorrect username or password', category='error')
        return render_template('login.html', form=login_form)
    else:
        return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    session['logged_in_admin'] = False
    flash('You have been logged out successfully.', category='logout-success')
    return redirect(url_for('login'))
# Login/Logout Function END


# Account Management START
@app.route('/retrieve_admin', methods=['GET', 'POST'])
def retrieve_admin():
    if (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:    
        try:
            users_dict = {}
            db = shelve.open('database/users.db', 'r')
            users_dict = db['Users']
            db.close()

            users_list = []
            # if session.get('user_id') is not None:
            #     users_list.append(users_dict.get(session.get('user_id')))
            for key in users_dict:
                user = users_dict.get(key)
                users_list.append(user)

            return render_template('retrieve_admin.html', count=len(users_list), users_list=users_list)
        except:
            print("Error1")


@app.route('/updateAdmin/<int:id>/', methods=['GET', 'POST'])  # exception
def update_admin(id):
    update_user_form = CreateAdminForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        regex = r'[^A-Za-z0-9]+'        
        regex2 = r'[^A-Za-z0-9\s]+[@.]'        
        try:
            users_dict = {}
            db = shelve.open('database/users.db', 'w')
            users_dict = db['Users']
        except:
            print("Error")

        update_full_name = update_user_form.full_name.data
        update_gender = update_user_form.gender.data
        update_email = update_user_form.email.data
        update_mobile_no = update_user_form.mobile_no.data
        update_username = update_user_form.username.data
        update_password = update_user_form.password.data
        update_confirm_password = update_user_form.confirm_password.data

        if users_dict:
            for key in users_dict:
                content = users_dict[key]
                # when username already taken
                if update_username == content.get_username():
                    flash("Username already taken.", category='error')
                    return render_template('updateUser.html', form=update_user_form)
                # when the input has special characters
                if re.findall(regex, update_username) or re.findall(regex2, update_full_name) or re.findall(regex, update_mobile_no) or re.findall(regex2, update_email) or re.findall(regex, update_password) or re.findall(regex, update_confirm_password):
                    print("special characters found in update admin information form")                    
                    flash("No special characters for input fields allowed.", category='error')                    
                    return render_template('updateUser.html', form=update_user_form)
            else:
                update_password_digest = bcrypt.hashpw(update_password.encode(), bcrypt.gensalt())
                update_confirm_password_digest = bcrypt.hashpw(update_confirm_password.encode(), bcrypt.gensalt())
                update_password_digest = update_confirm_password_digest

                user = users_dict.get(id)
                user.set_full_name(update_full_name)
                user.set_gender(update_gender)
                user.set_email(update_email)
                user.set_mobile_no(update_mobile_no)            
                user.set_username(update_username)
                user.set_password(update_password_digest)
                user.set_confirm_password(update_confirm_password_digest)

                db['Users'] = users_dict
                db.close()
                print("Admin information updated.")
                flash("Admin information successfully updated!", category='success')

            return redirect(url_for('retrieve_admin'))                
            # return render_template('updateUser.html', form=update_user_form)        
    else:
        try:
            users_dict = {}
            db = shelve.open('database/users.db', 'r')
            users_dict = db['Users']
        except:
            print("Error")

            update_password_digest = bcrypt.hashpw(update_password.encode(), bcrypt.gensalt())
            update_confirm_password_digest = bcrypt.hashpw(update_confirm_password.encode(), bcrypt.gensalt())
            update_password_digest = update_confirm_password_digest

            user = users_dict.get(id)
            user.set_full_name(update_full_name)
            user.set_gender(update_gender)
            user.set_email(update_email)
            user.set_mobile_no(update_mobile_no)            
            user.set_username(update_username)
            user.set_password(update_password_digest)
            user.set_confirm_password(update_confirm_password_digest)

            db['Users'] = users_dict
            db.close()
            flash("Admin information successfully updated!", category='success')
            # return render_template('updateUser.html', form=update_user_form)
            return redirect(url_for('retrieve_admin'))
    return render_template('updateAdmin.html', form=update_user_form)


@app.route('/account-creation', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)  # what is this again?
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        regex = r'[^A-Za-z0-9]+' 
        regex2 = r'[^A-Za-z\s]+' # for full name
        regex3 = r'[^0-9]' # for postal code and mobile
        db = shelve.open('database/users.db', 'c')  # check, scan dict for existing

        try:
            users_dict = db['Users']  # retrieve
        except:
            print("Error in retrieving Users from 'user.db'.")  # pop-up error
        username = create_user_form.username.data
        fullName = create_user_form.full_name.data
        password = create_user_form.password.data
        confirm_password = create_user_form.confirm_password.data
        mobile = create_user_form.mobile_no.data
        gender = create_user_form.gender.data
        email = create_user_form.email.data
        postal_code = create_user_form.postal_code.data
        member = create_user_form.member.data        

        if users_dict:
            for key in list(users_dict.keys()):
                content = users_dict[key]
                # when the user information is already in database
                if username == content.get_username() or fullName == content.get_full_name() or mobile == content.get_mobile_no() or email == content.get_email() or postal_code == content.get_postal_code():
                    flash("User information already registered. Please register new information.", category='error')
                    return render_template('account-creation.html', form=create_user_form)
                # when username already taken
                elif username == content.get_username():
                    flash("Username already taken.", category='error')
                    return render_template('account-creation.html', form=create_user_form)
                # when full name has numbers
                elif re.findall(regex2, fullName) != []:
                    print("Full name has numbers!")
                    flash("Invalid full name! Enter alphabets!", category='error')
                    return render_template('account-creation.html', form=create_user_form)
                # when passwords don't match
                elif password != confirm_password:
                    print("passwords don't match!")
                    flash("Passwords don't match!", category='error')
                    return render_template('account-creation.html', form=create_user_form)
                # when postal_code or mobile number not numbers
                elif re.findall(regex3, postal_code) != [] or re.findall(regex3, mobile) != []:
                    print("Mobile or postal code inputs in account-creation page are not numbers!")
                    flash("Invalid mobile number or postal code!", category='error')
                    return render_template('account-creation.html', form=create_user_form)                
                # when the input has special characters
                elif re.findall(regex2, username) != [] or re.findall(regex2, fullName) != [] or re.findall(regex3, mobile) != [] or re.findall(regex3, postal_code) != [] or re.findall(regex, password) != [] or re.findall(regex, confirm_password) != []:
                    print(re.findall(regex2, username), re.findall(regex2, fullName), re.findall(regex, mobile), re.findall(regex, postal_code), re.findall(regex, password), re.findall(regex, confirm_password))
                    flash("No special characters for input fields allowed.", category='error')                    
                    return render_template('account-creation.html', form=create_user_form)
                # when email has invalid format
                try:
                    check_email = validate_email(email)
                    print(check_email.email)
                except EmailNotValidError:
                    print("Invalid email format!")
                    flash("Invalid email format!", category='error')
                    return render_template('account-creation.html', form=create_user_form)

                password_digest = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                confirm_password_digest = bcrypt.hashpw(confirm_password.encode(), bcrypt.gensalt())
                password_digest = confirm_password_digest
                users = User.User(fullName, gender, email, mobile, postal_code, username, password_digest, confirm_password_digest, member)

                count_id = 0

                try:
                    for key in users_dict:
                        count_id = key
                        count_id += 1
                        users.set_user_id(count_id)
                except:
                    count_id += 1
                    users.set_user_id(count_id)

                users_dict[users.get_user_id()] = users  # get user id
                db['Users'] = users_dict

                # Test codes
                users_dict = db['Users']
                user = users_dict[users.get_user_id()]
                print(user.get_full_name(), "was stored in user.db successfully with user_id ==", user.get_user_id())
                db.close()


        else:
            password_digest = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            confirm_password_digest = bcrypt.hashpw(confirm_password.encode(), bcrypt.gensalt())
            password_digest = confirm_password_digest
            users = User.User(fullName, gender, email, mobile, postal_code, username, password_digest, confirm_password_digest, member)

            count_id = 0

            try:
                for key in users_dict:
                    count_id = key
                    count_id += 1
                    users.set_user_id(count_id)
            except:
                count_id += 1
                users.set_user_id(count_id)

            users_dict[users.get_user_id()] = users  # get user id
            db['Users'] = users_dict

            # Test codes
            users_dict = db['Users']
            user = users_dict[users.get_user_id()]
            print(user.get_full_name(), "was stored in user.db successfully with user_id ==", user.get_user_id())
            db.close()

        return redirect(url_for('login'))
    return render_template('account-creation.html', form=create_user_form)


@app.route('/retrieveUsers')  # exception
@login_required
def retrieve_users():
    try:
        users_dict = {}
        db = shelve.open('database/users.db', 'r')
        users_dict = db['Users']
        db.close()

        users_list = []
        if session.get('user_id') is not None:
            users_list.append(users_dict.get(session.get('user_id')))
        # for key in users_dict:
        #     user = users_dict.get(key)
        #     users_list.append(user)

        return render_template('retrieve_user.html', count=len(users_list), users_list=users_list)
    except:
        print("Error1")


@app.route('/updateUser/<int:id>/', methods=['GET', 'POST']) # exception
def update_user(id):
    update_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        regex = r'[^A-Za-z0-9]+'         
        regex2 = r'[^A-Za-z0-9\s]+[@.]'         
        try:
            users_dict = {}
            db = shelve.open('database/users.db', 'w')
            users_dict = db['Users']
        except:
            print("Error")

        update_full_name = update_user_form.full_name.data
        update_gender = update_user_form.gender.data
        update_email = update_user_form.email.data
        update_mobile_no = update_user_form.mobile_no.data
        update_username = update_user_form.username.data
        update_password = update_user_form.password.data
        update_confirm_password = update_user_form.confirm_password.data

        if users_dict:
            for key in users_dict:
                content = users_dict[key]
                # when username already taken
                if update_username == content.get_username():
                    flash("Username already taken.", category='error')
                    return render_template('updateUser.html', form=update_user_form)
                # when the input has special characters
                if re.findall(regex, update_username) or re.findall(regex2, update_full_name) or re.findall(regex, update_mobile_no) or re.findall(regex2, update_email) or re.findall(regex, update_password) or re.findall(regex, update_confirm_password):
                    print(re.findall(regex, update_username))
                    print(re.findall(regex, update_full_name))
                    print(re.findall(regex, update_mobile_no))
                    print(re.findall(regex, update_email))
                    print(re.findall(regex, update_password))
                    print(re.findall(regex, update_confirm_password))

                    print("special characters found in update user information form")
                    flash("No special characters for input fields allowed.", category='error')                    
                    return render_template('updateUser.html', form=update_user_form)
                    
            else:
                update_password_digest = bcrypt.hashpw(update_password.encode(), bcrypt.gensalt())
                update_confirm_password_digest = bcrypt.hashpw(update_confirm_password.encode(), bcrypt.gensalt())
                update_password_digest = update_confirm_password_digest

                user = users_dict.get(id)
                user.set_full_name(update_full_name)
                user.set_gender(update_gender)
                user.set_email(update_email)
                user.set_mobile_no(update_mobile_no)            
                user.set_username(update_username)
                user.set_password(update_password_digest)
                user.set_confirm_password(update_confirm_password_digest)

                db['Users'] = users_dict
                db.close()
                print("User information updated.")
                flash("User information successfully updated!", category='success')
            
            return redirect(url_for('retrieve_admin'))

            # return render_template('updateUser.html', form=update_user_form)        
    else:
        try:
            users_dict = {}
            db = shelve.open('database/users.db', 'r')
            users_dict = db['Users']
        except:
            print("Error")

            update_password_digest = bcrypt.hashpw(update_password.encode(), bcrypt.gensalt())
            update_confirm_password_digest = bcrypt.hashpw(update_confirm_password.encode(), bcrypt.gensalt())
            update_password_digest = update_confirm_password_digest

            user = users_dict.get(id)
            user.set_full_name(update_full_name)
            user.set_gender(update_gender)
            user.set_email(update_email)
            user.set_mobile_no(update_mobile_no)            
            user.set_username(update_username)
            user.set_password(update_password_digest)
            user.set_confirm_password(update_confirm_password_digest)

            db['Users'] = users_dict
            db.close()
            flash("User information successfully updated!", category='success')
            # return render_template('updateUser.html', form=update_user_form)
            return redirect(url_for('retrieve_admin'))
    return render_template('updateUser.html', form=update_user_form)        

@app.route('/deleteUser/<int:id>', methods=['POST']) # exception
def delete_user(id):
    try:
        users_dict = {}
        db = shelve.open('database/users.db', 'w')
        users_dict = db['Users']

        users_dict.pop(id)

        db['Users'] = users_dict
        db.close()
    
        return redirect(url_for('retrieve_admin'))
    except:
        print("Error")
# Account Management END

# Buy Car START
@app.route('/buy-car', methods=['GET', 'POST'])
def buy_car():
    regex = r'[^A-Za-z0-9\s]+'     
    search_form = SearchBar(request.form)   
    create_cars_dict = {}
    db = shelve.open('database/createCar.db', 'r')
    create_cars_dict = db['Createcars']
    db.close()

    createCar_list = []
    for key in create_cars_dict:
        cars = create_cars_dict.get(key)
        createCar_list.append(cars)
    
    if request.method == "POST" and search_form.validate():
        search = search_form.search.data
        # check for special characters
        print(re.findall(regex, search))
        if re.findall(regex, search) != []:
            print("Special characters found in search bar!")
            error = "405 Method Not Allowed"
            method_not_allowed(error)
            return render_template('error405.html'), 405
        else:
            return redirect(url_for('buy_car'))


    return render_template('buy-car.html', count=len(createCar_list), createCar_list=createCar_list)
# Buy Car END


# Browse Listings START
@app.route('/browse-listings')
def browse_listings():
    sellcars_dict = {}
    db = shelve.open('database/sellcar.db', 'r')
    sellcars_dict = db['Sellcars']
    db.close()

    sellcar_list = []
    for key in sellcars_dict:
        sellcar = sellcars_dict.get(key)
        sellcar_list.append(sellcar)

    return render_template('browse-listings.html', count=len(sellcar_list), sellcar_list=sellcar_list)
# Browse Listings END


# Product Page START
@app.route('/product-page')
def product():
    return render_template('product-page.html')
# Product Page END


# Sell Car Page START
@app.route('/sell-your-car', methods=['GET', 'POST'])
@login_required
def sell_your_car():
    sell_car_form = CreateSellCarForm(request.form)
    if request.method == 'POST' and sell_car_form.validate():
        sellcars_dict = {}
        db = shelve.open('database/sellcar.db', 'c')

        try:
            sellcars_dict = db['Sellcars']
        except:
            print("Error in retrieving Sellcars from sellcar.db.")

        Sellcar = sellcar.Sellcar(sell_car_form.car_model.data, sell_car_form.car_brand.data, sell_car_form.car_price.data, sell_car_form.condition.data, sell_car_form.remarks.data)

        count_id = 0
        try:
            for key in sellcars_dict:
                count_id = key
                count_id += 1
                Sellcar.set_sellcar_id(count_id)
        except:
            count_id += 1
            Sellcar.set_sellcar_id

        sellcars_dict[Sellcar.get_sellcar_id()] = Sellcar
        db['Sellcars'] = sellcars_dict

        # Test codes
        sellcars_dict = db['Sellcars']
        Sellcar = sellcars_dict[Sellcar.get_sellcar_id()]
        print(Sellcar.get_car_model(), Sellcar.get_car_brand(), "was stored in sellcar.db successfully with sellcar_id ==", Sellcar.get_sellcar_id())

        db.close()

        return redirect(url_for('browse_listings'))
    return render_template('sell-your-car.html', form=sell_car_form)
# Sell Car Page END


# Support Forum Codes START
@app.route('/support-forum')
def support_forum():
    # Announcements START
    announcements_dict = {}

    try:
        db = shelve.open('database/announcements.db', 'r')
        announcements_dict = db['Announcements']
        db.close()
    except:
        print("Error in retrieving Announcements from 'announcements.db'.")

    announcements_list = []
    for key in announcements_dict:
        announcements = announcements_dict.get(key)
        announcements_list.append(announcements)
    # Announcements END

    # Threads START
    threads_dict = {}

    try:
        db = shelve.open('database/threads.db', 'r')
        threads_dict = db['Threads']
        db.close()
    except:
        print("Error in retrieving Threads from 'threads.db'.")

    threads_list = []
    for key in threads_dict:
        threads = threads_dict.get(key)
        threads_list.append(threads)
    # Threads END
    return render_template('support-forum.html', count=len(threads_list), announcements_list=announcements_list[::-1], threads_list=threads_list[::-1])


@app.route('/thread-creation', methods=['GET', 'POST'])
def create_thread():
    if (session['logged_in'] == True) or (session['logged_in_admin'] == True):
        create_thread_form = CreateThread(request.form)
        if request.method == 'POST' and create_thread_form.validate():
            threads_dict = {}
            users_dict = {}
            regex = r'[^A-Za-z0-9\s.,!]+'    

            thread_username = create_thread_form.thread_username.data
            thread_title = create_thread_form.thread_title.data
            thread_message = create_thread_form.thread_message.data
            thread_reply = create_thread_form.thread_reply.data
            
            db = shelve.open('database/users.db', 'r')
            users_dict = db['Users']

            # check if username exists in database
            
            db = shelve.open('database/threads.db', 'c')

            try:
                threads_dict = db['Threads']
            except:
                print("Error in retrieving Threads from 'threads.db'.")
            
            # check if thread inputs have special characters
            if re.findall(regex, thread_username) == [] and re.findall(regex, thread_title) == [] and re.findall(regex, thread_message):
                threads = Thread.Thread(thread_username, thread_title, thread_message, thread_reply)

                count_id = 0

                try:
                    for key in threads_dict:
                        count_id = key
                        count_id += 1
                        threads.set_thread_id(count_id)
                except:
                    count_id += 1
                    threads.set_thread_id(count_id)

                threads_dict[threads.get_thread_id()] = threads
                db['Threads'] = threads_dict

                # Thread Creation Program Recording Code START
                threads_dict = db['Threads']
                threads = threads_dict[threads.get_thread_id()]
                print(threads.get_thread_title(), "was stored in 'threads.db' successfully with thread_id ==", threads.get_thread_id())
                # Thread Creation Program Recording Code END

                db.close()

            else:
                print(re.findall(regex, thread_username), re.findall(regex, thread_title), re.findall(regex, thread_message))
                print("Special characters found in created thread")
                flash("No special characters allowed in input fields.", category='error')  
                return render_template('thread-creation.html', form=create_thread_form)


            return redirect(url_for('support_forum'))
        return render_template('thread-creation.html', form=create_thread_form)
    else:
        return redirect(url_for('authentication_required'))


@app.route('/view-thread/<int:id>/', methods=['GET', 'POST'])
def view_thread(id):
    view_thread_form = CreateThread(request.form)
    if request.method == "POST" and view_thread_form.validate():
        threads_dict = {}
        print(threads_dict)
        db = shelve.open('database/threads.db', 'w')

        try:
            threads_dict = db['Threads']
        except:
            print("Error in retrieving Threads from 'threads.db'.")

        try:
            thread = threads_dict.get(id)
            thread.set_thread_username(view_thread_form.thread_username.data)
            thread.set_thread_title(view_thread_form.thread_title.data)
            thread.set_thread_message(view_thread_form.thread_message.data)
            thread.set_thread_reply(view_thread_form.thread_reply.data)
        except:
            thread = threads_dict.get(id)
            thread.set_thread_username(view_thread_form.thread_username.data)
            thread.set_thread_title(view_thread_form.thread_title.data)
            thread.set_thread_message(view_thread_form.thread_message.data)

        db['Threads'] = threads_dict
        db.close()

        return redirect(url_for('support_forum'))
    else:
        threads_dict = {}
        db = shelve.open('database/threads.db', 'r')

        try:
            threads_dict = db['Threads']
        except:
            print("Error in retrieving Threads from 'threads.db'.")

        db.close()

        try:
            thread = threads_dict.get(id)
            view_thread_form.thread_title.data = thread.get_thread_title()
            view_thread_form.thread_username.data = thread.get_thread_username()
            view_thread_form.thread_message.data = thread.get_thread_message()
            view_thread_form.thread_reply.data = thread.get_thread_reply()
        except:
            thread = threads_dict.get(id)
            view_thread_form.thread_title.data = thread.get_thread_title()
            view_thread_form.thread_username.data = thread.get_thread_username()
            view_thread_form.thread_message.data = thread.get_thread_message()

        return render_template('view-thread.html', form=view_thread_form)


@app.route('/update-thread/<int:id>/', methods=['GET', 'POST'])
def update_thread(id):
    if session['logged_in_admin'] == True:
        update_thread_form = CreateThread(request.form)
        if request.method == "POST" and update_thread_form.validate():
            regex = r'[^A-Za-z0-9\s.,!]+' 
            threads_dict = {}
            db = shelve.open('database/threads.db', 'w')

            try:
                threads_dict = db['Threads']
            except:
                print("Error in retrieving Threads from 'threads.db'.")

            thread_username = update_thread_form.thread_username.data
            thread_title = update_thread_form.thread_title.data
            thread_message = update_thread_form.thread_message.data
            thread_reply = update_thread_form.thread_reply.data
            if re.findall(regex, thread_username) == [] and re.findall(regex, thread_title) == [] and re.findall(regex, thread_message) == [] and re.findall(regex, thread_reply) == []:
                print(re.findall(regex, thread_username), re.findall(regex, thread_title), re.findall(regex, thread_message), re.findall(regex, thread_reply))                
                print("No special characters found in update support thread form.")

                try:
                    thread = threads_dict.get(id)
                    thread.set_thread_username(thread_username)
                    thread.set_thread_title(thread_title)
                    thread.set_thread_message(thread_message)
                    thread.set_thread_reply(thread_reply)
                except:
                    thread = threads_dict.get(id)
                    thread.set_thread_username(thread_username)
                    thread.set_thread_title(thread_title)
                    thread.set_thread_message(thread_message)

                db['Threads'] = threads_dict
                db.close()

                return redirect(url_for('support_forum'))
            else:
                print(re.findall(regex, thread_username), re.findall(regex, thread_title), re.findall(regex, thread_message), re.findall(regex, thread_reply))                
                print("Special characters found in update support thread form.")
                flash("No special chracters allowed in input fields!", category='error')
                return render_template('update-thread.html', form=update_thread_form)
        else:
            threads_dict = {}
            db = shelve.open('database/threads.db', 'r')

            try:
                threads_dict = db['Threads']
            except:
                print("Error in retrieving Threads from 'threads.db'.")

            db.close()

            try:
                thread = threads_dict.get(id)
                update_thread_form.thread_title.data = thread.get_thread_title()
                update_thread_form.thread_username.data = thread.get_thread_username()
                update_thread_form.thread_message.data = thread.get_thread_message()
                update_thread_form.thread_reply.data = thread.get_thread_reply()
            except:
                thread = threads_dict.get(id)
                update_thread_form.thread_title.data = thread.get_thread_title()
                update_thread_form.thread_username.data = thread.get_thread_username()
                update_thread_form.thread_message.data = thread.get_thread_message()

            return render_template('update-thread.html', form=update_thread_form)
    else:
        return redirect(url_for('admin_authentication_required'))


@app.route('/delete-thread/<int:id>', methods=['POST'])
def delete_thread(id):
    if session['logged_in_admin'] == True:
        threads_dict = {}
        db = shelve.open('database/threads.db', 'w')
        threads_dict = db['Threads']

        threads_dict.pop(id)

        db['Threads'] = threads_dict
        db.close()

        return redirect(url_for('support_forum'))
    else:
        return redirect(url_for('admin_authentication_required'))


@app.route('/announcement-creation', methods=['GET', 'POST'])
def create_announcement():
    if session['logged_in_admin'] == True:
        create_announcement_form = CreateAnnouncement(request.form)
        if request.method == 'POST' and create_announcement_form.validate():
            announcements_dict = {}
            regex = r'[^A-Za-z0-9\s.,!]+' 
            db = shelve.open('database/announcements.db', 'c')

            try:
                announcements_dict = db['Announcements']
            except:
                print("Error in retrieving Announcements from 'announcements.db'.")
            thread_username = create_announcement_form.thread_username.data
            thread_title = create_announcement_form.thread_title.data
            thread_message = create_announcement_form.thread_message.data
            thread_reply = create_announcement_form.thread_reply.data
            announcement_type = create_announcement_form.announcement_type.data
            severity_level = create_announcement_form.severity_level.data

            # check for special characters
            if re.findall(regex, thread_username) == [] and re.findall(regex, thread_title) == [] and re.findall(regex, thread_message) == [] and re.findall(regex, thread_reply) == [] and re.findall(regex, announcement_type) == [] and re.findall(regex, severity_level):
                announcements = Announcement.Announcement(thread_username, thread_title, thread_message, thread_reply, announcement_type, severity_level)

                count_id = 0

                try:
                    for key in announcements_dict:
                        count_id = key
                        count_id += 1
                        announcements.set_announcement_id(count_id)
                except:
                    count_id += 1
                    announcements.set_announcement_id(count_id)

                announcements_dict[announcements.get_announcement_id()] = announcements
                db['Announcements'] = announcements_dict

                # Announcement Creation Program Recording Code START
                announcements_dict = db['Announcements']
                announcements = announcements_dict[announcements.get_announcement_id()]
                print(announcements.get_thread_title(), "was stored in 'announcements.db' successfully with announcement_id ==", announcements.get_announcement_id())
                # Announcement Creation Program Recording Code END
                    
                db.close()

            else:
                print("Special characters found in announcements")                
                flash("No special characters allowed in input fields.")
                return redirect(url_for('support_forum'))
            
            return redirect(url_for('support_forum'))
        return render_template('announcement-creation.html', form=create_announcement_form)
    else:
        return redirect(url_for('admin_authentication_required'))


@app.route('/delete-announcement/<int:id>', methods=['POST'])
def delete_announcement(id):
    if session['logged_in_admin'] == True:
        announcements_dict = {}
        db = shelve.open('database/announcements.db', 'w')
        announcements_dict = db['Announcements']

        announcements_dict.pop(id)

        db['Announcements'] = announcements_dict
        db.close()

        return redirect(url_for('support_forum'))
    else:
        return redirect(url_for('admin_authentication_required'))
# Support Forum Codes END

# Product Purchase START
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if (session['logged_in'] == True) or (session['logged_in_admin'] == True):
        create_order_form = CreateOrderForm(request.form)
        secret_key = get_fixed_key() # get the fixed secret key
        if request.method == 'POST' and create_order_form.validate():
            orders_dict = {}
            users_dict = {}
            regex = r'[^A-Za-z0-9]+'    
            regex2 = r'[^A-Za-z0-9\s]' 
            name_list = []
            payment_list = []

            postal_code = create_order_form.postal_code.data
            card_name = create_order_form.card_name.data
            card_no = create_order_form.card_no.data
            expmonth = create_order_form.expmonth.data
            expyear = create_order_form.expyear.data
            cvv = create_order_form.cvv.data
            
            # check if card name and postal code is valid in database or not
            db = shelve.open('database/users.db', 'r')
            users_dict = db['Users']
            
            for key in users_dict:
                content = users_dict[key]
                name_list.append((content.get_full_name(), content.get_postal_code()))
            print(set(name_list))
            db.close()

            db = shelve.open('database/orders.db', 'c')
            try:
                orders = db['Orders']
                orders_dict = orders
            except:
                print("Error retrieving orders from Order.py.")

            if orders_dict:
                for key in orders_dict.copy():
                    content = orders_dict[key]
                    print(re.findall(regex, postal_code), re.findall(regex2, card_name), re.findall(regex, card_no), re.findall(regex, expmonth), re.findall(regex, expyear), re.findall(regex, cvv))
                    if re.findall(regex, postal_code) == [] and re.findall(regex2, card_name) == [] and re.findall(regex, card_no) == [] and re.findall(regex, expmonth) == [] and re.findall(regex, expyear) == [] and re.findall(regex, cvv) == []:
                        if (card_name, postal_code) not in name_list: # when the card name is valid
                            # get the order_id of the customer
                            print("Invalid postal code or name on card!")
                            flash("Invalid name on card or postal code!", category='error')
                            return render_template('checkout.html', form=create_order_form)
                        print("Inside If statement. Name inside list.")

                        # check if payment details match.

                        # encrypt the inputs and store in database
                        cipher_postal_code = encrypt(secret_key, postal_code.encode("utf8"))
                        cipher_card_name = encrypt(secret_key, card_name.encode("utf8"))
                        cipher_card_no = encrypt(secret_key, card_no.encode("utf8"))
                        cipher_expmonth = encrypt(secret_key, expmonth.encode("utf8"))
                        cipher_expyear = encrypt(secret_key, expyear.encode("utf8"))
                        cipher_cvv = encrypt(secret_key, cvv.encode("utf8"))
                        orders = Order.Order(cipher_postal_code, cipher_card_name, cipher_card_no, cipher_expmonth, cipher_expyear, cipher_cvv)                                            
                        count_id = 0

                        try:
                            for key in orders_dict:
                                count_id = key
                                count_id += 1
                                orders.set_order_id(count_id)
                        except:
                            count_id += 1
                            orders.set_order_id(count_id)
                    
                        orders_dict[orders.get_order_id()] = orders
                        print("orders_dict after: ", orders_dict)
                        db['Orders'] = orders_dict
                        # Test codes
                        orders = orders_dict[orders.get_order_id()]
                        print(decrypt(get_fixed_key(), orders.get_card_name()).decode(), "was stored in 'orders.db' successfully with order_id ==", orders.get_order_id())
                        db.close()
                                            
                    else: # when have special characters
                        print("Special characters found in create orders form.")
                        flash("No special characters for input fields allowed.", category='error')                    
                        return render_template('checkout.html', form=create_order_form) 

            else: # if not order_dict
                print(re.findall(regex, postal_code), re.findall(regex2, card_name), re.findall(regex, card_no), re.findall(regex, expmonth), re.findall(regex, expyear), re.findall(regex, cvv))
                if re.findall(regex, postal_code) == [] and re.findall(regex2, card_name) == [] and re.findall(regex, card_no) == [] and re.findall(regex, expmonth) == [] and re.findall(regex, expyear) == [] and re.findall(regex, cvv) == []:
                    # append all full names to Fullname list
                    db = shelve.open('database/users.db', 'r')
                    try:
                        users_dict = db['Users']
                    except:
                        print("Error retrieving users from User.py.")
                    
                    for key in users_dict:
                        content = users_dict[key]
                        name_list.append((content.get_full_name(), content.get_postal_code()))
                    print(set(name_list))
                    db.close()
                    
                    if (card_name, postal_code) not in name_list:
                        print("Invalid card name or postal code!")  
                        flash("Invalid postal code or name on card!", category='error')
                        return render_template('checkout.html', form=create_order_form)
                    
                    # check if credit card details match
                    print("Inside Else statement, orders_dict before: " ,orders_dict)                    

                    db = shelve.open('database/orders.db', 'c')
                    print("Inside Else statement. Name inside list.")
                    # encrypt the inputs and store in database
                    cipher_postal_code = encrypt(secret_key, postal_code.encode("utf8"))
                    cipher_card_name = encrypt(secret_key, card_name.encode("utf8"))
                    cipher_card_no = encrypt(secret_key, card_no.encode("utf8"))
                    cipher_expmonth = encrypt(secret_key, expmonth.encode("utf8"))
                    cipher_expyear = encrypt(secret_key, expyear.encode("utf8"))
                    cipher_cvv = encrypt(secret_key, cvv.encode("utf8"))
                    orders = Order.Order(cipher_postal_code, cipher_card_name, cipher_card_no, cipher_expmonth, cipher_expyear, cipher_cvv)                                            
                    count_id = 0

                    try:
                        for key in orders_dict:
                            count_id = key
                            count_id += 1
                            orders.set_order_id(count_id)
                            
                    except:
                        count_id += 1
                        orders.set_order_id(count_id)
                        
                    
                    orders_dict[orders.get_order_id()] = orders
                    print("orders_dict after: ", orders_dict)
                    db['Orders'] = orders_dict
                    # Test codes
                    orders = orders_dict[orders.get_order_id()]
                    print(decrypt(get_fixed_key(), (orders.get_card_name())).decode(), "was stored in 'orders.db' successfully with order_id ==", orders.get_order_id())
                    db.close()
                else: # when there are special characters
                    print("Special characters found in create orders form.")
                    flash("No special characters for input fields allowed.", category='error')                    
                    return render_template('checkout.html', form=create_order_form) 

            return redirect(url_for('order_confirmation'))
    return render_template('checkout.html', form=create_order_form)
# Product Purchase END


# Order Confirmation Page START
@app.route('/order-confirmation')
def order_confirmation():
    secret_key = get_fixed_key()
    orders_dict = {}
    try:
        db = shelve.open('database/orders.db', 'r')
        orders_dict = db['Orders']
        db.close()
    except:
        print("Error in retrieving Orders from 'orders.db'.")
    
    orders_list = []
    for key in orders_dict:
        orders = orders_dict.get(key)
        # print(orders.get_postal_code()) # this prints the ciphertext of postal code
        # decrypt all data in orders 
        plain_postal_code = decrypt(secret_key, orders.get_postal_code()).decode()
        plain_card_name = decrypt(secret_key, orders.get_card_name()).decode()
        plain_card_no = decrypt(secret_key, orders.get_card_no()).decode()
        plain_expmonth = decrypt(secret_key, orders.get_expmonth()).decode()
        plain_expyear = decrypt(secret_key, orders.get_expyear()).decode()
        plain_cvv = decrypt(secret_key, orders.get_cvv()).decode()
        orders = Order.Order(plain_postal_code, plain_card_name, plain_card_no, plain_expmonth, plain_expyear, plain_cvv)
        orders_list.append(orders)    
    return render_template('order-confirmation.html', count=len(orders_list), orders_list=orders_list[::-1])
# Order Confirmation Page END


# Order History START
@app.route('/retrieveOrder')
def retrieve_order():
    if session['logged_in'] == True:
        orders_dict = {}
        secret_key = get_fixed_key()
        try:
            db = shelve.open('database/orders.db', 'r')
            orders_dict = db['Orders']
            db.close()

        except:
            print("Error in retrieving Orders from 'orders.db'.")

        orders_list = []
        for key in orders_dict:
            orders = orders_dict.get(key)
            plain_postal_code = decrypt(secret_key, orders.get_postal_code()).decode()
            plain_card_name = decrypt(secret_key, orders.get_card_name()).decode()
            plain_card_no = decrypt(secret_key, orders.get_card_no()).decode()
            plain_expmonth = decrypt(secret_key, orders.get_expmonth()).decode()
            plain_expyear = decrypt(secret_key, orders.get_expyear()).decode()
            plain_cvv = decrypt(secret_key, orders.get_cvv()).decode()
            orders = Order.Order(plain_postal_code, plain_card_name, plain_card_no, plain_expmonth, plain_expyear, plain_cvv)            
            orders_list.append(orders)

        return render_template('retrieveOrder.html', count=len(orders_list), orders_list=orders_list[::-1])
    else:
        return render_template('authentication-required.html')
# Order History END

# Delete Order START
@app.route('/deleteOrder/<int:id>', methods=['POST'])
def delete_order(id):
    orders_dict = {}
    db = shelve.open('database/orders.db', 'w')
    try:
        orders_dict = db['Orders']
    except:
        print("Error in retrieving Orders from orders.db.")

    orders_dict.pop(id)

    db['Orders'] = orders_dict
    db.close()

    return redirect(url_for('retrieve_order'))
# Delete Order END


# Retrieve Sell Cars START
@app.route('/retrieveSellCars')
def retrieve_sellcars():
    if session['logged_in_admin'] == False:
        return render_template('admin-authentication-required.html')
    else:
        sellcars_dict = {}
        db = shelve.open('database/sellcar.db', 'r')
        try:
            sellcars_dict = db['Sellcars']
            db.close()
        except:
            print("Error in retrieving Sellcars from sellcar.db.")

        sellcar_list = []
        for key in sellcars_dict:
            sellcar = sellcars_dict.get(key)
            sellcar_list.append(sellcar)

        return render_template('retrieveSellCars.html', count=len(sellcar_list), sellcar_list=sellcar_list)
# Retrieve Sell Cars END


# Update Sell Cars START
@app.route('/updateSellCars/<int:id>/', methods=['GET', 'POST'])
def update_sellcars(id):
    if (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        update_sellcars = CreateSellCarForm(request.form)
        if request.method == 'POST' and update_sellcars.validate():
            regex = r'[^A-Za-z0-9\s.,!]+' 
            db = shelve.open('database/sellcar.db', 'w')
            sellcars_dict = db['Sellcars']

            car_brand = update_sellcars.car_brand.data
            car_model = update_sellcars.car_model.data
            car_price = update_sellcars.car_price.data
            remarks = update_sellcars.remarks.data
            condition = update_sellcars.condition.data
            print(re.findall(regex, car_model), re.findall(regex, remarks))
            
            if re.findall(regex, car_model) == [] and re.findall(regex, remarks) == []:                
                sellcar = sellcars_dict.get(id)
                sellcar.set_car_brand(car_brand)
                sellcar.set_car_model(car_model)
                sellcar.set_car_price(car_price)
                sellcar.set_condition(condition)
                sellcar.set_remarks(remarks)

                db['Sellcars'] = sellcars_dict
                db.close()
                
                flash("Car information successfully updated!", category='success')
                return redirect(url_for('retrieve_sellcars'))

            else:
                print("Special characters found in Update sell car form")
                flash("No special characters allowed in input fields!", category='error')
                return render_template('updateSellCars.html', form=update_sellcars)

        else:
            sellcars_dict = {}
            db = shelve.open('database/sellcar.db', 'r')
            sellcars_dict = db['Sellcars']
            db.close()

            sellcar = sellcars_dict.get(id)
            update_sellcars.car_brand.data = sellcar.get_car_brand()
            update_sellcars.car_model.data = sellcar.get_car_model()
            update_sellcars.car_brand.data = sellcar.get_car_price()
            update_sellcars.condition.data = sellcar.get_condition()
            update_sellcars.car_remarks = sellcar.get_remarks()

            return render_template('updateSellCars.html', form=update_sellcars)
# Update Sell Cars END

# Delete Sell Cars START
@app.route('/deleteSellCars/<int:id>', methods=['POST'])
def delete_sellcar(id):
    if (session['logged_in_admin'] == False):
        return render_template('authentication-required.html')
    else:
        sellcars_dict = {}
        db = shelve.open('database/sellcar.db', 'w')
        try:
            sellcars_dict = db['Sellcars']
        except:
            print("Error in retrieving Sellcars from sellcar.db.")

        sellcars_dict.pop(id)

        db['Sellcars'] = sellcars_dict
        db.close()

        return redirect(url_for('retrieve_sellcars'))
# Delete Sell Cars END


# Car Page START
@app.route('/createCar', methods=['GET', 'POST'])
def create_car():
    if (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        create_car_form = CreateCarsForm(request.form)
        if request.method == 'POST' and create_car_form.validate():
            create_cars_dict = {}
            regex = r'[^A-Za-z0-9\s.,!]+' 
            
            carModel = create_car_form.car_model.data
            carBrand = create_car_form.car_brand.data
            carPrice = create_car_form.car_price.data

            if re.findall(regex, carModel) == [] and re.findall(regex, carPrice) == []:
                # check if car information already exist in database
                db = shelve.open('database/createCar.db', 'r') # open database for reading
                create_cars_dict = db['Createcars']

                for key, value in create_cars_dict.items():
                    if (carModel == value.get_car_model() and carBrand == value.get_car_brand() and carPrice == value.get_car_price()) or (carModel == value.get_car_model() and carBrand == value.get_car_brand()):
                        print("car already exists!")
                        flash("This car model already exists!", category='error')
                        return render_template('createCar.html', form=create_car_form)
                db.close()

                db = shelve.open('database/createCar.db', 'c') # open database for creating car

                try:
                    create_cars_dict = db['Createcars']
                except:
                    print("Error in retrieving Createcars from createCar.db.")


                Createcar = Cars.Cars(carModel, carBrand, carPrice)
                count_id = 0
                
                try:
                    for key in create_cars_dict:
                        count_id = key
                        count_id += 1
                        Createcar.set_car_id(count_id)
                except:
                    count_id += 1
                    Createcar.set_car_id

                create_cars_dict[Createcar.get_car_id()] = Createcar
                db['Createcars'] = create_cars_dict

                # Test codes
                create_cars_dict = db['Createcars']
                Createcar = create_cars_dict[Createcar.get_car_id()]
                print(Createcar.get_car_model(), Createcar.get_car_brand(), "was stored in sellcar.db successfully with sellcar_id ==", Createcar.get_car_id())
                flash("Car successfully created!", category='success')

                db.close()
                return redirect(url_for('admin_dashboard'))

            else:
                print(re.findall(regex, carModel), re.findall(regex, carPrice))
                print("Special characters found in order inputs.")
                flash("No special characters allowed in input fields.", category='error')
                return render_template('createCar.html', form=create_car_form)

        return render_template('createCar.html', form=create_car_form)
# Car Page END


# Admin Retrieve Cars START
@app.route('/adminRetrieveCars')
def admin_retrieve_cars():
    if (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        create_cars_dict = {}
        db = shelve.open('database/createCar.db', 'r')
        create_cars_dict = db['Createcars']
        db.close()

        createCar_list = []
        for key in create_cars_dict:
            cars = create_cars_dict.get(key)
            createCar_list.append(cars)

        return render_template('adminRetrieveCars.html', count=len(createCar_list), createCar_list=createCar_list)
# Admin Retrieve Cars END


# Update create cars start
@app.route('/adminUpdateCars/<int:id>/', methods=['GET', 'POST'])
def update_cars(id):
    if (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        update_cars = CreateCarsForm(request.form)
        if request.method == 'POST' and update_cars.validate():
            regex = r'[^A-Za-z0-9\s.,!]+'
            db = shelve.open('database/createCar.db', 'w')
            create_cars_dict = db['Createcars']

            car_brand = update_cars.car_brand.data
            car_model = update_cars.car_model.data
            car_price = update_cars.car_price.data

            if re.findall(regex, car_model) == [] and re.findall(regex, car_price) == []:
                create_car = create_cars_dict.get(id)
                create_car.set_car_brand(car_brand)
                create_car.set_car_model(car_model)
                create_car.set_car_price(car_price)

                db['Createcars'] = create_cars_dict
                db.close()

                flash("Car information successfully updated!", category='success')
                return redirect(url_for('admin_retrieve_cars'))

            else:
                print(re.findall(regex, car_model), re.findall(regex, car_price))
                print("Special characters found in update call to sell form")
                flash("No special characters allowed in input fields!", category='error')
                return render_template('adminUpdateCars.html', form=update_cars)

        else:
            create_cars_dict = {}
            db = shelve.open('database/createCar.db', 'r')
            create_cars_dict = db['Createcars']
            db.close()

            create_car = create_cars_dict.get(id)
            create_car.set_car_brand(update_cars.car_brand.data)
            create_car.set_car_model(update_cars.car_model.data)
            create_car.set_car_price(update_cars.car_price.data)

            return render_template('adminUpdateCars.html', form=update_cars)
# Update create cars END


# Delete create Cars START
@app.route('/deleteCars/<int:id>', methods=['POST'])
def delete_car(id):
    if (session['logged_in'] == False) or (session['logged_in'] == True) or (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        Create_cars_dict = {}
        db = shelve.open('database/Createcar.db', 'w')
        try:
            Create_cars_dict = db['Createcars']
        except:
            print("Error in retrieving createcars from Createcar.db.")

        Create_cars_dict.pop(id)

        db['Createcars'] = Create_cars_dict
        db.close()

        return redirect(url_for('admin_retrieve_cars'))
# Delete create Cars END


# Admin Page START
@app.route('/admin-dashboard')
def admin_dashboard():
    if session['logged_in_admin'] == True:
        return render_template('admin-dashboard.html')
    else:
        return redirect(url_for('admin_authentication_required'))


@app.route('/dashboard')
def sales():
    if (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        orders_dict = {}

        try:
            db = shelve.open('database/orders.db', 'r')
            orders_dict = db['Orders']
            db.close()

        except:
            print("Error in retrieving Orders from 'orders.db'.")

        orders_list = []
        for key in orders_dict:
            orders = orders_dict.get(key)
            orders_list.append(orders)

        return render_template('dashboard.html', count=len(orders_list), orders_list=orders_list[::-1])
# Admin Page END

# Sales Order Deletion START
@app.route('/deleteOrderAdmin/<int:id>', methods=['POST'])
def delete_order_admin(id):
    if ((session['logged_in'] == False) or (session['logged_in'] == True)) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        orders_dict = {}
        db = shelve.open('database/orders.db', 'w')
        try:
            orders_dict = db['Orders']
        except:
            print("Error in retrieving Orders from orders.db.")

        orders_dict.pop(id)

        db['Orders'] = orders_dict
        db.close()

        return redirect(url_for('sales'))
# Sales Order END

# Footer Link Routing START
@app.route('/order-refund-policy')
def order_refund_policy():
    return render_template('order-refund-policy.html')


@app.route('/terms-of-use')
def terms_of_use():
    return render_template('terms-of-use.html')


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')
# Footer Link Routing END


# IMPORTANT: ALL CODES MUST BE ADDED BEFORE THIS LINE/COMMENT
if __name__ == '__main__':
    app.run(debug=True)
