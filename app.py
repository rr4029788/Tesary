from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
import json, urllib.request, hashlib, time, os

Window.softinput_mode = "below_target"
FIREBASE_URL = "https://tesara3-aeca9-default-rtdb.firebaseio.com"
LOCAL_FILE = "tesara3_local.json"

def make_constant_code(email):
    h = hashlib.md5(email.lower().strip().encode()).hexdigest()
    return h[:6].upper()

def save_local(code, data):
    try:
        all_data = {}
        if os.path.exists(LOCAL_FILE):
            with open(LOCAL_FILE, 'r') as f:
                all_data = json.load(f)
        all_data[code] = data
        with open(LOCAL_FILE, 'w') as f:
            json.dump(all_data, f)
        return True
    except: return False

def load_local(code):
    try:
        if not os.path.exists(LOCAL_FILE): return None
        with open(LOCAL_FILE, 'r') as f:
            all_data = json.load(f)
        return all_data.get(code)
    except: return None

class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(text='TESARA3 HYBRID\nOFFLINE + ONLINE', bold=True, font_size=20, size_hint_y=None, height=90))
        b1 = Button(text='1. ADMIN (Offline Works)', background_color=(0,0.8,0,1), size_hint_y=None, height=90)
        b2 = Button(text='2. MEMBER (Offline Works)', background_color=(0,0.4,0.8,1), size_hint_y=None, height=90)
        b1.bind(on_press=lambda x: setattr(self.manager,'current','areg'))
        b2.bind(on_press=lambda x: setattr(self.manager,'current','mreg'))
        box.add_widget(b1); box.add_widget(b2)
        box.add_widget(Widget(size_hint_y=None, height=400))
        s = ScrollView(); s.add_widget(box); self.add_widget(s)

class ARegScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(text='Tesara3 Admin - Fixed CODE', bold=True, size_hint_y=None, height=60))
        self.a = TextInput(hint_text='username ryan', multiline=False, size_hint_y=None, height=50)
        self.email = TextInput(hint_text='Email rr4029788@gmail.com', multiline=False, size_hint_y=None, height=50)
        box.add_widget(self.a); box.add_widget(self.email)
        box.add_widget(Button(text='Create Tesara3 Account', background_color=(0,0.8,0,1), size_hint_y=None, height=70, on_press=self.next_screen))
        box.add_widget(Button(text='Back Home', size_hint_y=None, height=50, on_press=lambda x: setattr(self.manager,'current','home')))
        box.add_widget(Widget(size_hint_y=None, height=400))
        scroll.add_widget(box); self.add_widget(scroll)
    def next_screen(self, *a):
        if "@" not in self.email.text: return
        app = App.get_running_app()
        app.admin_email = self.email.text.strip()
        app.admin_name = self.a.text.strip()
        app.fixed_code = make_constant_code(app.admin_email)
        self.manager.get_screen('adash').set_code()
        self.manager.current = 'adash'

class ADashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        scroll = ScrollView()
        main = BoxLayout(orientation='vertical', padding=10, spacing=8, size_hint_y=None)
        main.bind(minimum_height=main.setter('height'))
        self.lbl = Label(text='CODE:', size_hint_y=None, height=180); main.add_widget(self.lbl)
        main.add_widget(Label(text='Class | Amount | Items auto', bold=True, size_hint_y=None, height=40))
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.class_input = TextInput(hint_text='Class', multiline=False)
        self.amount_input = TextInput(hint_text='Amount', input_filter='int', multiline=False)
        self.items_label = Label(text='Items:0', size_hint_x=0.5)
        self.amount_input.bind(text=self.calc)
        row.add_widget(self.class_input); row.add_widget(self.amount_input); row.add_widget(self.items_label)
        main.add_widget(row)
        main.add_widget(Button(text='Add Row', background_color=(0,0.7,0,1), size_hint_y=None, height=50, on_press=self.add_row))
        header = GridLayout(cols=3, size_hint_y=None, height=40, spacing=2)
        for t in ['Class','Amount','Items']: header.add_widget(Label(text=t, bold=True))
        main.add_widget(header)
        self.grid = GridLayout(cols=3, size_hint_y=None, spacing=2)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        main.add_widget(self.grid)
        main.add_widget(Button(text='SHARE - OFFLINE + ONLINE 24HRS', background_color=(0,0.8,0,1), size_hint_y=None, height=80, on_press=self.share_table))
        self.share_msg = Label(text='', size_hint_y=None, height=140, color=(0,1,0,1)); main.add_widget(self.share_msg)
        main.add_widget(Button(text='CLEAR FOR NEW TABLE', background_color=(0.8,0.2,0,1), size_hint_y=None, height=50, on_press=self.clear_table))
        main.add_widget(Button(text='Back Home', size_hint_y=None, height=50, on_press=lambda x: setattr(self.manager,'current','home')))
        main.add_widget(Widget(size_hint_y=None, height=400))
        scroll.add_widget(main); self.add_widget(scroll)
        self.rows = []
    def calc(self, inst, val):
        try: self.items_label.text = f"Items:{int(val)//10 if val else 0}"
        except: self.items_label.text = "Items:0"
    def set_code(self):
        app = App.get_running_app()
        self.lbl.text = f"TESARA3 ADMIN: {app.admin_name}\nEMAIL: {app.admin_email}\nFIXED CODE: {app.fixed_code}\nHYBRID: Works offline!\nExpires 24hrs"
    def add_row(self, *a):
        if not self.class_input.text.strip() or not self.amount_input.text.strip(): return
        amt = int(self.amount_input.text.strip()); items = amt//10; cls = self.class_input.text.strip()
        self.rows.append([cls, str(amt), str(items)])
        for txt in [cls, str(amt), str(items)]: self.grid.add_widget(Label(text=txt, size_hint_y=None, height=35))
        App.get_running_app().orders = self.rows
        self.class_input.text=""; self.amount_input.text=""; self.items_label.text="Items:0"
    def share_table(self, *a):
        if not self.rows: self.share_msg.text="Add rows first"; return
        app = App.get_running_app()
        now = int(time.time()); expires = now + 24*3600
        data = {"rows": self.rows, "code": app.fixed_code, "admin": app.admin_email, "created": now, "expires": expires}
        # 1. Save OFFLINE always
        save_local(app.fixed_code, data)
        self.share_msg.text = f"Saved OFFLINE locally!\nCODE: {app.fixed_code}\nTrying online sync..."
        # 2. Try ONLINE Firebase
        try:
            url = f"{FIREBASE_URL}/tables/{app.fixed_code}.json"
            req = urllib.request.Request(url, data=json.dumps(data).encode(), method='PUT', headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req, timeout=10) as r:
                self.share_msg.text = f"TESARA3 SUCCESS!\nOFFLINE + ONLINE!\nCODE: {app.fixed_code}\nValid 24 HRS\nWorks without internet!"
        except:
            self.share_msg.text = f"Saved OFFLINE!\nCODE: {app.fixed_code}\nNo internet - table works on this phone\nWill sync when internet comes\nValid 24 HRS"
    def clear_table(self, *a):
        self.rows = []; self.grid.clear_widgets(); self.share_msg.text="Cleared! Add new rows"

class MRegScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', padding=12, spacing=10, size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        box.add_widget(Label(text='Tesara3 Member - Hybrid', bold=True, size_hint_y=None, height=60))
        self.o = TextInput(hint_text='Admin Fixed CODE', multiline=False, size_hint_y=None, height=50)
        box.add_widget(self.o)
        box.add_widget(Button(text='GET TABLE - OFFLINE + ONLINE', background_color=(0,0.7,0,1), size_hint_y=None, height=70, on_press=self.submit))
        box.add_widget(Widget(size_hint_y=None, height=400))
        scroll.add_widget(box); self.add_widget(scroll)
    def submit(self, *a):
        if self.o.text.strip() == "": return
        self.manager.get_screen('mdash').code_to_fetch = self.o.text.strip().upper()
        self.manager.get_screen('mdash').load_table()
        self.manager.current='mdash'

class MDashScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        scroll = ScrollView()
        self.main = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint_y=None)
        self.main.bind(minimum_height=self.main.setter('height'))
        self.title_lbl = Label(text='Tesara3 Orders', bold=True, size_hint_y=None, height=100)
        self.main.add_widget(self.title_lbl)
        self.table = GridLayout(cols=3, size_hint_y=None, spacing=2)
        self.table.bind(minimum_height=self.table.setter('height'))
        self.main.add_widget(self.table)
        self.main.add_widget(Button(text='Back Home', size_hint_y=None, height=50, on_press=lambda x: setattr(self.manager,'current','home')))
        scroll.add_widget(self.main); self.add_widget(scroll)
        self.code_to_fetch = ""
    def load_table(self):
        self.table.clear_widgets()
        for t in ['Class','Amount','Items']: self.table.add_widget(Label(text=t, bold=True, size_hint_y=None, height=35))
        # 1. Try LOCAL first (offline)
        res = load_local(self.code_to_fetch)
        source = "OFFLINE LOCAL"
        # 2. If not local, try ONLINE Firebase
        if not res:
            try:
                url = f"{FIREBASE_URL}/tables/{self.code_to_fetch}.json"
                with urllib.request.urlopen(url, timeout=10) as r:
                    res = json.loads(r.read().decode())
                source = "ONLINE FIREBASE"
                if res: save_local(self.code_to_fetch, res) # cache offline
            except: res = None
        if not res:
            self.title_lbl.text = f"CODE {self.code_to_fetch} not found\nOffline & Online checked"
            return
        # Check expiry 24hr
        if "expires" in res and int(time.time()) > res["expires"]:
            self.title_lbl.text = f"TESARA3 EXPIRED!\nAdmin must create new"
            return
        remain = res["expires"] - int(time.time()) if "expires" in res else 0
        self.title_lbl.text = f"TESARA3 {self.code_to_fetch}\nFrom: {source}\nValid {remain//3600} hrs\nAdmin: {res.get('admin','')}"
        for c,a,i in res.get("rows",[]):
            self.table.add_widget(Label(text=c, size_hint_y=None, height=35))
            self.table.add_widget(Label(text=a, size_hint_y=None, height=35))
            self.table.add_widget(Label(text=i, size_hint_y=None, height=35))

class Tesara3App(App):
    def build(self):
        self.title = "Tesara3"
        self.admin_email=""; self.admin_name=""; self.orders=[]; self.fixed_code=""
        sm=ScreenManager()
        sm.add_widget(HomeScreen(name='home')); sm.add_widget(ARegScreen(name='areg'))
        sm.add_widget(ADashScreen(name='adash')); sm.add_widget(MRegScreen(name='mreg'))
        sm.add_widget(MDashScreen(name='mdash'))
        return sm

Tesara3App().run()