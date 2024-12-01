import pytest
@pytest.mark.asyncio
async def test_verify_email(test_client, test_token):
    response = await test_client.get(f"/verify-email/?token={test_token}")
    assert response.status_code == 200
    assert response.json() == {"msg": "Email verified successfully"}
