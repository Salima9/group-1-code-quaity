import mysql.connector as mysql
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.toast import toast

MYSQL_USER = 'root'  # USER-NAME
MYSQL_PASS = 'NewPassword'  # MYSQL_PASS
MYSQL_DATABASE = 'appproject'  # DATABASE_NAME

connection = mysql.connect(user=MYSQL_USER,
                           passwd=MYSQL_PASS,
                           database=MYSQL_DATABASE,
                           host='127.0.0.1')

cnx = connection.cursor(dictionary=True)


class PopMessages:
    """En klass med som har samtliga pop meddelanden"""

    def invalid_input(self):
        toast("Incorrect password or username", duration=2)

    def account_created(self):
        toast("You are now a member of Student Market", duration=2)

    def already_exisiting(self):
        toast("A user with this username exists already", duration=3)

    def salesAD_created(self):
        toast("A sales advertisement was sucessfully published", duration=4)

    def salesAD_removed(self):
        toast("A sales advertisement was sucessfully removed", duration=4)

    def salesAD_updated(self):
        toast('Your ad has been successfully updated', duration=2)

    def no_match(self):
        toast('learn to spell', duration=2)


class User:
    """Klass som skapar en avnändare"""
    created_password = StringProperty('')
    created_name = StringProperty('')
    PhoneNr = ObjectProperty()

    def __init__(self, name, password, phonenr):
        self.name = name
        self.password = password
        self.phonenr = phonenr

    def createUser(self):
        """Funktion som skapar en användare och lägger till i databasen"""
        try:
            cnx.execute(f"INSERT INTO User(email, password, phoneNr) Values('{self.name}',"
                        f" '{self.password}', '{self.phonenr}')")
            connection.commit()
            PopMessages().account_created()

        except:
            connection.close()
            PopMessages().already_exisiting()


class LoginPage(ScreenManager):
    """Klass som hanterar inloggningen"""

    def check_account(self, name, password):
        """Funktion som kollar ifall användaren finns i databasem. Om inte
        så skickas det ett fel meddelande"""
        try:
            password_variable = f"SELECT password FROM User WHERE email = '{name}'"
            cnx.execute(password_variable)
            password_query = cnx.fetchone()
            connection.commit()
            if password == password_query.get('password'):
                return True

            else:
                return False
        except:
            pass


class createAD:
    """ Klass som hanterar funktioner så som att skapa ad"""

    def __init__(self, headline, username, description, author, category, price, image):
        self.username = username
        self.description = description
        self.author = author
        self.category = category
        self.price = price
        self.headline = headline
        self.image = image

    def get_price(self):
        return self.price

    def get_userid_ad_list(self):
        """Funktionen retunerar den inloggades ID"""
        user_id = HomePage().get_user_id(self.username)
        return user_id

    def createAD(self):
        """Skapar en ad och sätter in i datasbasen"""

        user_id = HomePage().get_user_id(self.username)
        cnx.execute(
            f"INSERT INTO Sales_ad(headline, USER_id, description, author, category, price, image) "
            f"Values('{self.headline}',{user_id},'{self.description}',"
            f"'{self.author}','{self.category}',{self.price}, {self.image}")
        connection.commit()
        PopMessages().salesAD_created()


class adManager:

    def removeAD(self, adID):
        cnx.execute(f"SET SQL_SAFE_UPDATES = 0")
        delete = f"DELETE FROM Sales_ad Where Ad_id = '{adID}'"
        cnx.execute(delete)
        connection.commit()
        PopMessages().salesAD_removed()

    def get_all_Applications(self, *args):
        searchInput = f"SELECT * FROM Sales_ad"
        cnx.execute(searchInput)
        result = cnx.fetchall()
        connection.commit()
        return result


class HomePage(Screen):
    """Klass som har samtliga funktioner för appens sidor (exkluderat inlogg, skapa användare, skapa ad"""

    def get_user_phonenr(self, email):
        """Hämtar användarens telefonnummer"""
        try:
            """Funktion som returnerar användarens telefonnummer som en string"""
            user_phonenr = f"SELECT phoneNr FROM User Where email = '{email}'"
            cnx.execute(user_phonenr)
            user_query = cnx.fetchone()
            connection.commit()
            return str(user_query.get('phoneNr'))
        except:
            pass

    def get_user_id(self, name):
        """Hämtar användarens ID från databasen"""
        user_id = f"SELECT USER_ID FROM User WHERE email = '{name}'"
        cnx.execute(user_id)
        result = cnx.fetchone()
        connection.commit()
        return result.get('USER_ID')

    def get_all_ads(self, user_id):
        """Hämtar samtliga ads som skapats av användaren från databasen"""
        ad_info = f"SELECT * FROM Sales_ad WHERE USER_id = '{user_id}'"
        cnx.execute(ad_info)
        result = cnx.fetchall()
        connection.commit()
        return result

    def get_specific_ad(self, ad_id):
        """Hämtar en specfik ad som användaren skapat"""
        ad = f"SELECT * FROM Sales_ad WHERE Ad_id = '{ad_id}'"
        cnx.execute(ad)
        the_ad = cnx.fetchone()
        connection.commit()
        return the_ad

    def update_profile_info(self, ID, new_name, password, phonenr):
        """Uppdaterar användarens profil vid begäran"""
        cnx.execute(f"SET SQL_SAFE_UPDATES = 0")
        update = f"UPDATE  User SET email = '{new_name}', password = '{password}', phoneNr = {phonenr} " \
                 f"WHERE USER_ID = {ID}"
        cnx.execute(update)
        connection.commit()
        print(ID, new_name, password, phonenr)

    def update_ad(self, headline, dscrp, author, cat, price, ad_id):
        """Uppdaterar en specifik ad vid begäran"""
        cnx.execute(f"SET SQL_SAFE_UPDATES = 0")
        update = f"UPDATE Sales_ad SET headline = '{headline}', description = '{dscrp}', " \
                 f"author = '{author}', category = '{cat}', price = {price} where Ad_id = {ad_id}"
        cnx.execute(update)
        connection.commit()


class adImages:
    """Klass som hanterar de bilder som uppladdas"""
    pass
