import time

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconRightWidget, ThreeLineAvatarIconListItem

from main import User, LoginPage, PopMessages, HomePage, adManager, createAD
from search import SearchPopupMenu


class MainApp(MDApp):
    _current_ad_id = int
    search_menu = None
    image_obj = None
    """Klass för själva appen."""


    def build(self):
        """Build funktion som initierar samtliga filer"""
        self.sm = ScreenManager()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        self.sm.add_widget(Builder.load_file('KV/first_page.kv'))
        self.sm.add_widget(Builder.load_file('KV/login_page.kv'))
        self.sm.add_widget(Builder.load_file('KV/createAccount_page.kv'))
        self.sm.add_widget(Builder.load_file('KV/home_page.kv'))
        self.sm.add_widget(Builder.load_file('KV/createSalesAD_page.kv'))
        self.sm.add_widget(Builder.load_file('KV/removeAD_page.kv'))
        self.sm.add_widget(Builder.load_file('KV/camera.kv'))
        return self.sm

    def show_dialog(self, **kwargs):
        """Funktion som initierar ett sökfält och kallar sedan på getApplication() med textinput som argument"""
        self.search_menu = MDDialog(
            type='custom',
            size_hint=(1, .2),
            content_cls=SearchPopupMenu(),
            buttons=[MDFlatButton(text='Cancel'),
                     MDRaisedButton(text='Search',
                                    on_release=self.getApplication)]

        )

        self.search_menu.open()

    def capture(self):
        camera = self.sm.get_screen('camera_screen').ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        image = ("IMG_{}.png".format(timestr))
        camera.play = False
        self.image_obj = self.convertToBinaryData(image)

    def convertToBinaryData(self, file):
        with open(file, 'rb') as f:
            binaryData = f.read()

        return binaryData

    def getApplication(self, *args):
        """Funktion som kollar i Sales_ad om sökningen matchar något och retunerar om det finns"""
        input = self.search_menu.content_cls.ids.search_dialog.text
        applications = adManager().get_all_Applications()
        self.clear_widget('ad_container')
        for ele in applications:
            if input in ele.values():
                self.search_ads(HomePage().get_specific_ad(ele.get('Ad_id')))

    def account_labels(self):
        """Skapar ett objekt av klassen User med samtliga inparametrar"""
        name = self.sm.get_screen("create_account").ids.created_name.text
        password = self.sm.get_screen("create_account").ids.created_password.text
        phoneNr = self.sm.get_screen("create_account").ids.PhoneNr.text
        User(name, password, phoneNr).createUser()

    def amount_ad(self):
        """Skapar en lista under fliken PROFILE med användarens
        skapade ads och retunerar ID  på det ad man trycker på"""
        try:
            ad_list = HomePage().get_all_ads(HomePage().get_user_id(self.get_name()))
            for i in range(len(ad_list)):
                icon = IconRightWidget(icon='close', on_press=lambda *args, x=i: self.dropAD(ad_list[x].get('Ad_id')))
                item = ThreeLineAvatarIconListItem(text=f"{ad_list[i].get('Ad_id')}",
                                                   secondary_text=f"{ad_list[i].get('headline')}"
                                                   , tertiary_text=f"Price: {ad_list[i].get('price')}")

                item.add_widget(icon)
                item.bind(on_press=self.edit_ad_input)
                self.sm.get_screen('home_page').ids.container.add_widget(item)

        except:
            ValueError('ValueError')

    def search_ads(self, ad):
        """Visar ads som matchar sökordet från getApplication()"""
        item = ThreeLineAvatarIconListItem(text=f"{ad.get('Ad_id')}",
                                           secondary_text=f"{ad.get('headline')}"
                                           , tertiary_text=f"Price: {ad.get('price')}")

        self.sm.get_screen('home_page').ids.ad_container.add_widget(item)

    def set_homepage_ads(self):
        self.clear_widget('ad_container')
        appli = adManager().get_all_Applications()
        for i in range(len(appli)):
            item = ThreeLineAvatarIconListItem(text=f"{appli[i].get('Ad_id')}",
                                               secondary_text=f"{appli[i].get('headline')}"
                                               , tertiary_text=f"Price: {appli[i].get('price')}")

            self.sm.get_screen('home_page').ids.ad_container.add_widget(item)

    def dropAD(self, instance):
        """Skickar ad id till adManager.removeAD för att ta bort ad"""
        adManager().removeAD(instance)
        self.clear_widget('container')

    def edit_ad_input(self, instance):
        """Tar ad-ID som inparameter och sätter ADet's samtliga beskrivningar på EDIT-AD sidan"""
        ad_id = instance.text
        ad = HomePage().get_specific_ad(ad_id)
        self.sm.get_screen('home_page').ids.edit_headline.text = ad.get('headline')
        self.sm.get_screen("home_page").ids.edit_description.text = ad.get('description')
        self.sm.get_screen("home_page").ids.edit_author.text = ad.get('author')
        self.sm.get_screen("home_page").ids.edit_category.text = ad.get('category')
        self.sm.get_screen("home_page").ids.edit_price.text = str(ad.get('price'))
        self._current_ad_id = ad_id

    def update_ad_input(self):
        """Uppdaterar den nya AD-beskrivningen och skickar argumenten till salesAD_updated"""
        ad_id = self._current_ad_id
        headline = self.sm.get_screen('home_page').ids.edit_headline.text
        dscrp = self.sm.get_screen("home_page").ids.edit_description.text
        author = self.sm.get_screen("home_page").ids.edit_author.text
        cat = self.sm.get_screen("home_page").ids.edit_category.text
        price = self.sm.get_screen("home_page").ids.edit_price.text
        HomePage().update_ad(headline, dscrp, author, cat, price, ad_id)
        PopMessages().salesAD_updated()

    def clear_widget(self, widget_id):
        """Nollställer AD-listan"""
        self.sm.get_screen('home_page').ids[f"{widget_id}"].clear_widgets()

    def reset(self):
        """reset funktion som nollställer önskade textFields"""
        self.sm.get_screen('login').ids.user_password.text = ''
        self.sm.get_screen('login').ids.user_name.text = ''

    def get_name(self):
        return self.sm.get_screen("login").ids.user_name.text

    def get_password(self):
        return self.sm.get_screen("login").ids.user_password.text

    def get_phonenr(self):
        return HomePage().get_user_phonenr(self.get_name())

    def salesAD_publish(self):
        """Publiserar en skapad ad och skapar ett objekt från klassen adManager"""

        username = self.get_name()
        headline = self.sm.get_screen("createSalesAD").ids.headline.text
        description = self.sm.get_screen("createSalesAD").ids.created_description.text
        author = self.sm.get_screen("createSalesAD").ids.created_author.text
        category = self.sm.get_screen("createSalesAD").ids.created_category.text
        price = self.sm.get_screen("createSalesAD").ids.created_price.text
        image = self.image_obj
        createAD(headline, username, description, author, category, price, image).createAD()

    def update_profile(self):
        """Funktion som skickar den nya profil informationen till update_profile_info som sedan updaterar databasen"""
        old_name = self.get_name()
        name = self.sm.get_screen('home_page').ids.edit_user.text
        phoneNr = self.sm.get_screen('home_page').ids.profile_phone.text
        password = self.sm.get_screen('home_page').ids.profile_password.text
        user_id = HomePage().get_user_id(old_name)
        HomePage().update_profile_info(user_id, name, password, phoneNr)

    def login_input(self):
        """Funktion som hanterar login. Samt sätter användarens information på Profil skärmen"""
        old_name = self.get_name()
        valid = LoginPage().check_account(self.get_name(), self.get_password())
        if valid:
            self.root.current = 'home_page'
            self.set_homepage_ads()
            self.sm.get_screen('home_page').ids.profile_name.text = f"Welcome {old_name}!"
            self.sm.get_screen('home_page').ids.edit_user.text = old_name
            self.sm.get_screen('home_page').ids.profile_phone.text = self.get_phonenr()
            self.sm.get_screen('home_page').ids.profile_password.text = self.get_password()


        else:
            self.reset()
            PopMessages().invalid_input()


if __name__ == '__main__':
    MainApp().run()
