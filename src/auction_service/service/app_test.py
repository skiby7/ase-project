import app as main_app

tested_app = main_app.app

# User 1
main_app.mock_authentication = True 
main_app.mock_distro = True
main_app.mock_tux = True
main_app.mock_player_id = True