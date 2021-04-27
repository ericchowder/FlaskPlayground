from urlshort_bp import create_app

# test to find "shorten" on page
def test_shorten(client):
    # get data from '/' url
    response = client.get('/')
    # verify word "Shorten" exists in response
    assert b'Shorten' in response.data