from config import base_url, timeout


class TestItemAPI:

    # Проверка создания объявления и валидация его структуры ТС-001
    def test_create_and_retrieve_item(self, api_session):
        # Создаём
        payload = {
            "sellerID": 1,
            "name": "o",
            "price": 1,
            "statistics": {"likes": 5, "viewCount": 1, "contacts": 1}
        }
        create_resp = api_session.post(f"{base_url}/api/1/item", json=payload, timeout=timeout)
        assert create_resp.status_code == 200

        # Извлекаем ID
        status_text = create_resp.json()["status"]
        item_id = status_text.split(" - ")[-1]

        # Получаем и валидируем
        get_resp = api_session.get(f"{base_url}/api/1/item/{item_id}", timeout=timeout)
        assert get_resp.status_code == 200
        self._validate_item_response(get_resp.json())

    # Проверка получения объявления по его идентификатору ТС-002
    def test_get_item_by_id(self, api_session, created_item):
        item_id = created_item["status"].split(" - ")[-1]
        resp = api_session.get(f"{base_url}/api/1/item/{item_id}", timeout=timeout)
        assert resp.status_code == 200
        self._validate_item_response(resp.json())

    # Проверка получения всех объявлений по идентификатору продавца ТС-003
    def test_get_items_by_seller(self, api_session, unique_id_seller):
        resp = api_session.get(f"{base_url}/api/1/{unique_id_seller}/item", timeout=timeout)
        assert resp.status_code == 200

    # Проверка получения статистики по айтем id ТС-004
    def test_get_statistic(self, api_session, created_item):
        item_id = created_item["status"].split(" - ")[-1]

        for num in [1, 2]:
            resp = api_session.get(
                f"{base_url}/api/{num}/statistic/{item_id}",
                timeout=timeout
            )
            assert resp.status_code == 200
            self._validate_statistic_response(resp.json())

    # Прогон негативных сценариев ТС-005 - ТС-008
    def test_negative_cases(self, api_session):
        # 1 Отсутствует sellerID
        bad_payload = {
            "name": "Без sellerID",
            "price": 100,
            "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
        }
        resp = api_session.post(f"{base_url}/api/1/item", json=bad_payload, timeout=timeout)
        assert resp.status_code == 400

        # 2 Несуществующий ID
        fake_id = ""
        assert api_session.get(f"{base_url}/api/1/item/{fake_id}").status_code == 404
        assert api_session.get(f"{base_url}/api/1/statistic/{fake_id}").status_code == 404
        assert api_session.get(f"{base_url}/api/1/{fake_id}/item", timeout=timeout).status_code == 405

    ## Валидируем структуру объявления
    def _validate_item_response(self, data):
        assert isinstance(data, list) and len(data) == 1
        item = data[0]
        assert isinstance(item, dict)
        assert "id" in item and isinstance(item["id"], str)
        assert "sellerId" in item and isinstance(item["sellerId"], int)
        assert "name" in item and isinstance(item["name"], str)
        assert "price" in item and isinstance(item["price"], int)
        assert "statistics" in item and isinstance(item["statistics"], dict)
        assert "createdAt" in item and isinstance(item["createdAt"], str)

        stat = item["statistics"]
        assert all(
            key in stat and isinstance(stat[key], int)
            for key in ["likes", "viewCount", "contacts"]
        )

    ## Валидируем структуру статистики объявления
    def _validate_statistic_response(self, data):
        assert isinstance(data, list) and len(data) == 1
        stat = data[0]
        assert isinstance(stat, dict)
        assert all(
            key in stat and isinstance(stat[key], int)
            for key in ["likes", "viewCount", "contacts"]
        )
