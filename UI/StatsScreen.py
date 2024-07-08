from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from DB.connection import Connection
from kivy.storage.jsonstore import JsonStore
from kivy.clock import mainthread, Clock
from kivy.app import App

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.fetch_stats); 
        # Clock.schedule_once(self.fetch_stats, 2)
        
    @mainthread
    def fetch_stats(self, *args):
        print("stats fetched"); 
        stored_data = JsonStore("data.json")
        if stored_data.exists('user1'):
            data = Connection.getStats()
            # StatsScreen.playerName = str(stored_data.get('user1')['userName'])
            playerName = App.get_running_app().root.get_screen('stats').ids.playerName
            playerName.text = "Statistiques du jeu, joueur : "+str(stored_data.get('user1')['userName'])

            PVPtotalPLayed =  App.get_running_app().root.get_screen('stats').ids.PVPtotalPLayed
            PVPwins =  App.get_running_app().root.get_screen('stats').ids.PVPwins
            PVPwinsPercentagePB =  App.get_running_app().root.get_screen('stats').ids.PVPwinsPercentagePB
            PVPwinsPercentage =  App.get_running_app().root.get_screen('stats').ids.PVPwinsPercentage
            PVPlost =  App.get_running_app().root.get_screen('stats').ids.PVPlost
            PVPlostPB =  App.get_running_app().root.get_screen('stats').ids.PVPlostPB
            PVPlostPercentage =  App.get_running_app().root.get_screen('stats').ids.PVPlostPercentage
            PVPdraw =  App.get_running_app().root.get_screen('stats').ids.PVPdraw
            PVPdrawPB =  App.get_running_app().root.get_screen('stats').ids.PVPdrawPB
            PVPdrawPercentage =  App.get_running_app().root.get_screen('stats').ids.PVPdrawPercentage
            PVPbestScore =  App.get_running_app().root.get_screen('stats').ids.PVPbestScore
            PVPbestTime =  App.get_running_app().root.get_screen('stats').ids.PVPbestTime

            PVMtotalPLayed =  App.get_running_app().root.get_screen('stats').ids.PVMtotalPLayed
            PVMwins =  App.get_running_app().root.get_screen('stats').ids.PVMwins
            PVMwinsPercentagePB =  App.get_running_app().root.get_screen('stats').ids.PVMwinsPercentagePB
            PVMwinsPercentage =  App.get_running_app().root.get_screen('stats').ids.PVMwinsPercentage
            PVMlost =  App.get_running_app().root.get_screen('stats').ids.PVMlost
            PVMlostPB =  App.get_running_app().root.get_screen('stats').ids.PVMlostPB
            PVMlostPercentage =  App.get_running_app().root.get_screen('stats').ids.PVMlostPercentage
            PVMdraw =  App.get_running_app().root.get_screen('stats').ids.PVMdraw
            PVMdrawPB =  App.get_running_app().root.get_screen('stats').ids.PVMdrawPB
            PVMdrawPercentage =  App.get_running_app().root.get_screen('stats').ids.PVMdrawPercentage
            PVMbestScore =  App.get_running_app().root.get_screen('stats').ids.PVMbestScore
            PVMbestTime =  App.get_running_app().root.get_screen('stats').ids.PVMbestTime

            pvp = data[0]
            pvm = data[1]
            #pvp data
            PVPtotalPLayed.text = str(pvp[1])
            PVPwins.text = str(pvp[2])
            PVPlost.text = str(pvp[5])
            PVPdraw.text = str(pvp[6])
            if pvp[1] != 0:
                PVPwinsPercentagePB.value,PVPwinsPercentage.text = int(pvp[2]/pvp[1]*100), str(int(pvp[2]/pvp[1]*100))+"%"
                PVPlostPB.value, PVPlostPercentage.text = int(pvp[5]/pvp[1]*100), str(int(pvp[5]/pvp[1]*100))+"%"
                PVPdrawPB.value, PVPdrawPercentage.text = int(pvp[6]/pvp[1]*100), str(int(pvp[6]/pvp[1]*100))+"%"
            PVPbestScore.text = str(pvp[3])+"pts | "+str(divmod(pvp[7], 60)[0])+"m"+str(divmod(pvp[7], 60)[1])+"s" 
            
            PVPbestTime.text = str(divmod(pvp[8], 60)[0])+"m"+str(divmod(pvp[8], 60)[1])+"s"
            
            #pvm data
            PVMtotalPLayed.text = str(pvm[1])
            PVMwins.text = str(pvm[2])
            PVMlost.text = str(pvm[5])
            PVMdraw.text = str(pvm[6])
            if pvm[1] != 0:
                PVMwinsPercentagePB.value,PVMwinsPercentage.text = int(pvm[2]/pvm[1]*100), str(int(pvm[2]/pvm[1]*100))+"%"
                PVMlostPB.value, PVMlostPercentage.text = int(pvm[5]/pvm[1]*100), str(int(pvm[5]/pvm[1]*100))+"%"
                PVMdrawPB.value, PVMdrawPercentage.text = int(pvm[6]/pvm[1]*100), str(int(pvm[6]/pvm[1]*100))+"%"
            PVMbestScore.text = str(pvm[3])+"pts | "+str(divmod(pvm[7], 60)[0])+"m"+str(divmod(pvm[7], 60)[1])+"s" 
            
            PVMbestTime.text = str(divmod(pvm[8], 60)[0])+"m"+str(divmod(pvm[8], 60)[1])+"s"