from flask import Flask, render_template, request, redirect, url_for, flash, session
from User import User
from Forms import CreateThread, CreateUserForm, CreateSellCarForm, LoginForm, CreateOrderForm, CreateAnnouncement, CreateCarsForm
import shelve, User, Thread, sellcar, Order, Announcement, Cars, bcrypt, rsa, re
from flask_login import login_user, login_required, logout_user, LoginManager
admin = __import__("admin")


app = Flask(__name__)
app.secret_key = 'ff59a421971cd4de00539f85d307e6bb'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # If user is not logged in


@login_manager.user_loader
def load_user(id):
    db = shelve.open('users.db', 'r')
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


# Error 404 Handling START
@app.errorhandler(404)
def page_not_found(e):
    print(e)
    app.logger.error(f"error: {e}, route: {request.url}")
    return render_template('error404.html'), 404
# Error 404 Handling END

@app.route('/about_me')
def about():
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('authentication-required.html')
    else:
        try:
            users_dict = {}
            db = shelve.open('users.db', 'r')
            users_dict = db['Users']
            db.close()

            users_list = []
            if session.get('user_id') is not None:
                users_list.append(users_dict.get(session.get('user_id')))
            # for key in users_dict:
            #     user = users_dict.get(key)
            #     users_list.append(user)

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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        login_form = LoginForm(request.form)
        if request.method == "POST" and login_form.validate():
            username = login_form.username.data            
            password = login_form.password.data
            regex = re.compile("[$&+,:;=?@#|'<>.-^*()%!]")
            db = shelve.open('users.db', 'r')
            db_content = db['Users']
            for key in db_content:
                content = db_content[key]
                print(content)
                if username == content.get_username():
                    print("Username exist")
                    # check if password has special characters
                    if re.findall(regex, password):
                        flash("Incorrect username or password", category='error')
                    # this compares the digest of the password (when regiester for account) with the digest of the
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
                else:
                    print("Username does not exist")
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:    
        try:
            users_dict = {}
            db = shelve.open('users.db', 'r')
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
    update_user_form = CreateUserForm(request.form)
    if request.method == 'POST' and update_user_form.validate():
        try:
            users_dict = {}
            db = shelve.open('users.db', 'w')
            users_dict = db['Users']

            user = users_dict.get(id)
            user.set_full_name(update_user_form.full_name.data)
            user.set_gender(update_user_form.gender.data)
            user.set_email(update_user_form.email.data)
            user.set_mobile_no(update_user_form.mobile_no.data)
            user.set_address(update_user_form.address.data)
            user.set_postal_code(update_user_form.postal_code.data)
            user.set_username(update_user_form.username.data)
            user.set_password(update_user_form.password.data)
            user.set_confirm_password(update_user_form.confirm_password.data)
            
            db['Users'] = users_dict
            db.close()

            return redirect(url_for('retrieve_admin'))
        except:
            print("Error")
    else:
        try:
            users_dict = {}
            db = shelve.open('users.db', 'r')
            users_dict = db['Users']
            db.close()

            user = users_dict.get(id)
            update_user_form.full_name.data = user.get_full_name()
            update_user_form.email.data = user.get_email()
            update_user_form.gender.data = user.get_gender()
            update_user_form.address.data = user.get_address()
            update_user_form.mobile_no = user.get_mobile_no()
            update_user_form.postal_code.data = user.get_postal_code()
            update_user_form.username.data = user.get_username()
            update_user_form.password.data = user.get_password()
            update_user_form.confirm_password.data = user.get_confirm_password()

            return render_template('updateUser.html', form=update_user_form)
        except:
            print("Error")


@app.route('/account-creation', methods=['GET', 'POST'])
def create_user():
    create_user_form = CreateUserForm(request.form)  # what is this again?
    if request.method == 'POST' and create_user_form.validate():
        users_dict = {}
        db = shelve.open('users.db', 'c')  # check, scan dict for existing

        try:
            users_dict = db['Users']  # retrieve
        except:
            print("Error in retrieving Users from 'user.db'.")  # pop-up error
        username = create_user_form.username.data
        if users_dict:
            for key in users_dict:
                content = users_dict[key]
                if username == content.get_username():
                    flash('Username is already taken.', category='error')
                    return redirect(url_for('create_user'))
            else:
                # generate hash for password and confirm_password
                # encode password
                password = create_user_form.password.data
                confirm_password = create_user_form.confirm_password.data
                
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())                
                password = hashed_pw
                confirm_password = hashed_pw

                users = User.User(create_user_form.full_name.data,
                                create_user_form.gender.data,
                                create_user_form.email.data,
                                create_user_form.mobile_no.data,
                                create_user_form.address.data,
                                create_user_form.postal_code.data,
                                create_user_form.username.data,
                                password, 
                                confirm_password,
                                create_user_form.member.data)
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
            # generate hash for password and confirm_password
            # encode password
            password_hash = create_user_form.password.data
            confirm_password_hash = create_user_form.confirm_password.data
            
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())                
            password = hashed_pw
            confirm_password = hashed_pw # confirm password and password must have the same digest

            users = User.User(create_user_form.full_name.data,
                            create_user_form.gender.data,
                            create_user_form.email.data,
                            create_user_form.mobile_no.data,
                            create_user_form.address.data,
                            create_user_form.postal_code.data,
                            create_user_form.username.data,
                            password_hash, 
                            confirm_password_hash,
                            create_user_form.member.data)                       
                        
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
        db = shelve.open('users.db', 'r')
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
        try:
            users_dict = {}
            db = shelve.open('users.db', 'w')
            users_dict = db['Users']

            user.set_full_name(update_user_form.full_name.data)
            user.set_gender(update_user_form.gender.data)
            user.set_email(update_user_form.email.data)
            user.set_mobile_no(update_user_form.mobile_no.data)
            user.set_address(update_user_form.address.data)
            user.set_postal_code(update_user_form.postal_code.data)
            user.set_username(update_user_form.username.data)
            user.set_password(update_user_form.password.data)
            user.set_confirm_password(update_user_form.confirm_password.data)

            db['Users'] = users_dict
            db.close()

            return redirect(url_for('retrieve_users'))
        except:
            print("Error")
    else:
        try:
            users_dict = {}
            db = shelve.open('users.db', 'r')
            users_dict = db['Users']
            db.close()

            user = users_dict.get(id)
            update_user_form.full_name.data = user.get_full_name()
            update_user_form.email.data = user.get_email()
            update_user_form.gender.data = user.get_gender()
            update_user_form.address.data = user.get_address()
            update_user_form.mobile_no.data = user.get_mobile_no()
            update_user_form.mobile_no.data = user.get_mobile_no()
            update_user_form.postal_code.data = user.get_postal_code()
            update_user_form.username.data = user.get_username()
            update_user_form.password.data = user.get_password()
            update_user_form.confirm_password.data = user.get_confirm_password()

            return render_template('updateUser.html', form=update_user_form)
        except:
            print("Error")


@app.route('/deleteUser/<int:id>', methods=['POST']) # exception
def delete_user(id):
    try:
        users_dict = {}
        db = shelve.open('users.db', 'w')
        users_dict = db['Users']

        users_dict.pop(id)

        db['Users'] = users_dict
        db.close()

        return redirect(url_for('retrieve_users'))
    except:
        print("Error")
# Account Management END


# Buy Car START
@app.route('/buy-car')
def buy_car():
    create_cars_dict = {}
    db = shelve.open('createCar.db', 'r')
    create_cars_dict = db['Createcars']
    db.close()

    createCar_list = []
    for key in create_cars_dict:
        cars = create_cars_dict.get(key)
        createCar_list.append(cars)

    return render_template('buy-car.html', count=len(createCar_list), createCar_list=createCar_list)
# Buy Car END


# Browse Listings START
@app.route('/browse-listings')
def browse_listings():
    sellcars_dict = {}
    db = shelve.open('sellcar.db', 'r')
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
        db = shelve.open('sellcar.db', 'c')

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
        db = shelve.open('announcements.db', 'r')
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
        db = shelve.open('threads.db', 'r')
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
            db = shelve.open('threads.db', 'c')

            try:
                threads_dict = db['Threads']
            except:
                print("Error in retrieving Threads from 'threads.db'.")

            threads = Thread.Thread(create_thread_form.thread_username.data, create_thread_form.thread_title.data, create_thread_form.thread_message.data, create_thread_form.thread_reply.data)

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
        db = shelve.open('threads.db', 'w')

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
        db = shelve.open('threads.db', 'r')

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
            threads_dict = {}
            print(threads_dict)
            db = shelve.open('threads.db', 'w')

            try:
                threads_dict = db['Threads']
            except:
                print("Error in retrieving Threads from 'threads.db'.")

            try:
                thread = threads_dict.get(id)
                thread.set_thread_username(update_thread_form.thread_username.data)
                thread.set_thread_title(update_thread_form.thread_title.data)
                thread.set_thread_message(update_thread_form.thread_message.data)
                thread.set_thread_reply(update_thread_form.thread_reply.data)
            except:
                thread = threads_dict.get(id)
                thread.set_thread_username(update_thread_form.thread_username.data)
                thread.set_thread_title(update_thread_form.thread_title.data)
                thread.set_thread_message(update_thread_form.thread_message.data)

            db['Threads'] = threads_dict
            db.close()

            return redirect(url_for('support_forum'))
        else:
            threads_dict = {}
            db = shelve.open('threads.db', 'r')

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
        db = shelve.open('threads.db', 'w')
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
            db = shelve.open('announcements.db', 'c')

            try:
                announcements_dict = db['Announcements']
            except:
                print("Error in retrieving Announcements from 'announcements.db'.")

            announcements = Announcement.Announcement(create_announcement_form.thread_username.data, create_announcement_form.thread_title.data, create_announcement_form.thread_message.data, create_announcement_form.thread_reply.data, create_announcement_form.announcement_type.data, create_announcement_form.severity_level.data)

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

            return redirect(url_for('support_forum'))
        return render_template('announcement-creation.html', form=create_announcement_form)
    else:
        return redirect(url_for('admin_authentication_required'))


@app.route('/delete-announcement/<int:id>', methods=['POST'])
def delete_announcement(id):
    if session['logged_in_admin'] == True:
        announcements_dict = {}
        db = shelve.open('announcements.db', 'w')
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
    create_order_form = CreateOrderForm(request.form)
    if request.method == 'POST' and create_order_form.validate():
        orders_dict = {}
        db = shelve.open('orders.db', 'c')

        try:
            orders_dict = db['Orders']
        except:
            print("Error in retrieving Orders from 'orders.db'.")
        
        # encrypt the card_name, card_no, expmonth, expyear, cvv
        # encrypt the data with rsa
        publicKey, privateKey = rsa.newkeys(512) # define the key length when generated
        encrypted_card_name = rsa.encrypt((create_order_form.card_name.data).encode(), publicKey)
        encrypted_card_no = rsa.encrypt((create_order_form.card_no.data).encode(), publicKey)
        encrypted_expMonth = rsa.encrypt((create_order_form.expmonth.data).encode(), publicKey)
        encrypted_expYear = rsa.encrypt((create_order_form.expyear.data).encode(), publicKey)
        encrypted_CVV = rsa.encrypt((create_order_form.cvv.data).encode(), publicKey)

        # orders = Order.Order(create_order_form.address.data, 
        #                     create_order_form.postal_code.data,
        #                     encrypted_card_name,
        #                     encrypted_card_no,
        #                     encrypted_expMonth,
        #                     encrypted_expYear, 
        #                     encrypted_CVV)

        orders = Order.Order(create_order_form.address.data, 
                            create_order_form.postal_code.data,
                            create_order_form.card_name,
                            create_order_form.card_no,
                            create_order_form.expMonth,
                            create_order_form.expYear, 
                            create_order_form.cvv)

        
        orders_dict[orders.get_order_id()] = orders
        db['Orders'] = orders_dict

        # Test Codes
        orders_dict = db['Orders']
        orders = orders_dict[orders.get_order_id()]
        print(orders.get_card_name(), "was stored in 'orders.db' successfully with order_id ==", orders.get_order_id())
        db.close()
        for key, value in orders_dict.items():
            print(f"key is {key}")
            print(f"{key}:\naddress:{value.get_address()}\npostal code:{value.get_postal_code()}\ncard_name:{value.get_card_name()}\ncard_no:{value.get_card_no()}\nexpMonth:{value.get_expmonth()},\nexpYear:{value.get_expyear()}\ncvv:{value.get_cvv()}\n")

        return redirect(url_for('order_confirmation'))
    return render_template('checkout.html', form=create_order_form)
# Product Purchase END


# Order Confirmation Page START
@app.route('/order-confirmation')
def order_confirmation():
    orders_dict = {}
    publicKey, privateKey = rsa.newkeys(512)
    try:
        db = shelve.open('orders.db', 'r')
        orders_dict = db['Orders']
        db.close()
    except:
        print("Error in retrieving Orders from 'orders.db'.")
    
    orders_list = []
    for key in orders_dict:
        orders = orders_dict.get(key)
        orders_list.append(orders)

    return render_template('order-confirmation.html', count=len(orders_list), orders_list=orders_list[::-1])
# Order Confirmation Page END


# Order History START
@app.route('/retrieveOrder')
def retrieve_order():
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        orders_dict = {}

        try:
            db = shelve.open('orders.db', 'r')
            orders_dict = db['Orders']
            db.close()

        except:
            print("Error in retrieving Orders from 'orders.db'.")

        orders_list = []
        for key in orders_dict:
            orders = orders_dict.get(key)
            orders_list.append(orders)

        return render_template('retrieveOrder.html', count=len(orders_list), orders_list=orders_list[::-1])
# Order History END

# Delete Order START
@app.route('/deleteOrder/<int:id>', methods=['POST'])
def delete_order(id):
    orders_dict = {}
    db = shelve.open('orders.db', 'w')
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        sellcars_dict = {}
        db = shelve.open('sellcar.db', 'r')
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

    update_sellcars = CreateSellCarForm(request.form)
    if request.method == 'POST' and update_sellcars.validate():
        db = shelve.open('sellcar.db', 'w')
        sellcars_dict = db['Sellcars']

        sellcar = sellcars_dict.get(id)
        sellcar.set_car_brand(update_sellcars.car_brand.data)
        sellcar.set_car_model(update_sellcars.car_model.data)
        sellcar.set_car_brand(update_sellcars.car_price.data)
        sellcar.set_condition(update_sellcars.condition.data)
        sellcar.set_remarks(update_sellcars.remarks.data)

        db['Sellcars'] = sellcars_dict
        db.close()

        return redirect(url_for('retrieve_sellcars'))

    else:
        sellcars_dict = {}
        db = shelve.open('sellcar.db', 'r')
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
    sellcars_dict = {}
    db = shelve.open('sellcar.db', 'w')
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('authentication-required.html')
    else:
        create_car_form = CreateCarsForm(request.form)
        if request.method == 'POST' and create_car_form.validate():
            create_cars_dict = {}
            db = shelve.open('createCar.db', 'c')

            try:
                create_cars_dict = db['Createcars']
            except:
                print("Error in retrieving Createcars from createCar.db.")

            Createcar = Cars.Cars(create_car_form.car_model.data, create_car_form.car_brand.data, create_car_form.car_price.data)

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

            db.close()

            return redirect(url_for('home'))
        return render_template('createCar.html', form=create_car_form)
# Car Page END


# Admin Retrieve Cars START
@app.route('/adminRetrieveCars')
def admin_retrieve_cars():
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        create_cars_dict = {}
        db = shelve.open('createCar.db', 'r')
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        update_cars = CreateCarsForm(request.form)
        if request.method == 'POST' and update_cars.validate():
            db = shelve.open('createCar.db', 'w')
            create_cars_dict = db['Createcars']

            create_car = create_cars_dict.get(id)
            create_car.set_car_brand(update_cars.car_brand.data)
            create_car.set_car_model(update_cars.car_model.data)
            create_car.set_car_price(update_cars.car_price.data)


            db['Createcars'] = create_cars_dict
            db.close()

            return redirect(url_for('admin_retrieve_cars'))

        else:
            create_cars_dict = {}
            db = shelve.open('createCar.db', 'r')
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        Create_cars_dict = {}
        db = shelve.open('Createcar.db', 'w')
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        orders_dict = {}

        try:
            db = shelve.open('orders.db', 'r')
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
    if (session['logged_in'] == False) and (session['logged_in_admin'] == False):
        return render_template('admin-authentication-required.html')
    else:
        orders_dict = {}
        db = shelve.open('orders.db', 'w')
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
