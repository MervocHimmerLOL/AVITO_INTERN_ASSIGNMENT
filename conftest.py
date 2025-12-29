import random
import pytest
import requests
from config import base_url, timeout


# Фикстура сессии
@pytest.fixture
def api_session():
    session = requests.Session()
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    yield session
    session.close()


# Фикстура айди продавца
@pytest.fixture
def unique_id_seller():
    return random.randint(111111, 999999)


# Фикстура создания объявления (удаляется после использования)
@pytest.fixture
def created_item(api_session, unique_id_seller):
    payload = {
        "sellerID": unique_id_seller,
        "name": "Продукт",
        "price": random.randint(1, 999999),
        "statistics": {
            "likes": random.randint(1, 999999),
            "viewCount": random.randint(1, 999999),
            "contacts": random.randint(1, 999999)
        }
    }

    resp = api_session.post(f'{base_url}/api/1/item', json=payload, timeout=timeout)
    assert resp.status_code == 200, f'Ошибка при создании объявления: {resp.text}'
    item = resp.json()

    yield item

    try:
        api_session.delete(f'{base_url}/api/2/item/{item['id']}', timeout=timeout)
    except Exception:
        pass
