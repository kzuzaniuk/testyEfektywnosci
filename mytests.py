import logging
import json
import pytest
import requests
import logging
from simple_utils import generate_body, generate_random_email, generate_random_string, anonymous_get_request, CREATE_USER_PAYLOAD, CREATE_USER_POST_PAYLOAD, EDIT_POST_PAYLOAD
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig()

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

URL_V0 = "https://gorest.co.in/public-api/"
URL_V1 = "https://gorest.co.in/public/v1/"
URL_V2 = "https://gorest.co.in/public/v2/"

FILE_PATH = "test_large_post.txt"
GOREST_KEY = '14f71b67f988bb8851089198676fe17571efef92a193c295fc9aa74b1787739f'

HEADERS = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {GOREST_KEY}',
        'Content-Type': 'application/json'
    }

@pytest.mark.tc01
def test_efektywnosci(URL: str = URL_V2, request_url: str = "users", resource: str = "", request_method: str = "GET"):
    url = URL + request_url
    
    if resource:
        data = generate_body(resource)
        payload = json.dumps(data)
        # print(payload)
        # print(data)
        response = requests.request(request_method, url, headers=HEADERS, data=payload)
        # print(response.json())
    else:
        response = requests.request(request_method, url, headers=HEADERS)
    
    response_time_in_ms = response.elapsed.total_seconds() * 1000    
    request_code = response.status_code
    LOGGER.info(request_code)
    LOGGER.info(f"Czas odpowiedzi: {response_time_in_ms}ms")
    assert 200 <= request_code <= 203,"Failed somewhere"
    try:
        assert response_time_in_ms <= 200, "Za długo!"
    except AssertionError:
        LOGGER.warning("Długi czas oczekiwania")
        
test_efektywnosci()
test_efektywnosci(URL_V1)
test_efektywnosci(URL_V0)
test_efektywnosci(request_method="POST", resource="user")

#Spróbować z locustem https://locust.io/
@pytest.mark.tc02
def test_wiele_requestow(request_method: str = 'GET', URL: str = URL_V2, request_url: str = 'users', liczba_requestow: int = 100):
    url = URL + request_url
    def get_user(url):
        return requests.request(request_method, url, headers=HEADERS)
    list_of_urls = [url] * liczba_requestow
    
    # print(get_user())
    with ThreadPoolExecutor(max_workers=100) as pool:
        response_list = list(pool.map(get_user, list_of_urls)) #czyli dla każdego workera, wywołuje funkcje do zrobienia, drugi argument to po prostu lista adresów?
        for response in response_list:
            LOGGER.info(f"Kod odpowiedzi: {response.status_code}")
            LOGGER.info(f"Czas odpowiedzi przy {liczba_requestow} jednoczesnych requestach: {response.elapsed.total_seconds() * 1000}")
        
test_wiele_requestow()