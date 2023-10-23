from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


async def test_response_statuses():

    response_account_add = client.post('/account_add/')
    response_add_sources_to_existing_account = client.post('/add_sources_to_existing_account/')
    response_change_account_belonging_to_profile = client.put('change_account_belonging_to_profile')

    assert response_account_add.status_code == 200, 'Неверный статус сервера'
    assert response_add_sources_to_existing_account.status_code == 200, 'Неверный статус сервера'
    assert response_change_account_belonging_to_profile.status_code == 200, 'Неверный статус сервера'