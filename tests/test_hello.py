def hello(name):
    return f"Hello, {name}!"

def test_hello():
    assert hello("World") == "Hello, World!"
    assert hello("") == "Hello, !"
    assert hello("Alice") == "Hello, Alice!"