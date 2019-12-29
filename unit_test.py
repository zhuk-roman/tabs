import pytest
from tabs import bcrypt
from tabs.models import User


username = "patkennedy79"
email = "patkennedy79@gmail.com"
password = "FlaskIsAwesome"
hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')


@pytest.fixture(scope='module')
def new_user():
    new_user = User(username=username, email=email, password=hashed_password)
    return new_user

def test_new_user(new_user):
    assert new_user.username == username
    assert new_user.email == email
    assert new_user.password != password
    assert new_user.password == hashed_password
    assert new_user.tabs == []