from UI.console.menu_consola import MenuConsola
class ConsoleBase:
    def __init__(self, game_title: str):
        self.game_title = game_title
        self.menu = MenuConsola(self.game_title)
    
    def show_menu(self):
        self.menu.show_menu()
    
    def start_game(self):
        self.menu.start_game()
    
    def load_game(self):
        self.menu.load_game()
    pass