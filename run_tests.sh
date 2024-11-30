# This script allows you to test the services manually

PYTHONPATH=src/auction_service:src/auction_service/service pytest src/auction_service
PYTHONPATH=src/authentication_service:src/authentication_service/service pytest src/authentication_service
PYTHONPATH=src/gacha_service:src/gacha_service/service pytest src/gacha_service
PYTHONPATH=src/tux_service:src/tux_service/service pytest src/tux_service
