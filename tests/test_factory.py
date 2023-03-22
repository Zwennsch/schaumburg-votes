from voting import create_app

def test_config():
    print("in test_config of test_factory.py")
    assert not create_app().testing
    assert create_app({'TESTING':True}).testing
    