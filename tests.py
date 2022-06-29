from main import app
from globals import SHORT_URL_LENGTH
import secrets, string, json

# TODO - More elegant test framework (currently stops on failure and doesn't run the remaining tests)

TEST_URL_LENGTH=10

# Generate random test url
test_url = ("").join(secrets.choice(string.ascii_letters + string.digits) for _ in range(TEST_URL_LENGTH))

too_long_url = 'test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_url.com'

with app.test_client() as ta:
    # Create URL
    result1 = ta.post('/shorten?URL=' + test_url)
    assert(result1.status_code == 201)
    shortcode_result = result1.data.decode('UTF-8')[-SHORT_URL_LENGTH:]

    # Repeat with same URL
    result2 = ta.post('/shorten?URL=' + test_url)
    assert(result2.status_code == 303)

    # Try with too long URL
    result3 = ta.post('/shorten?URL=' + too_long_url)
    assert(result3.status_code == 404)

    # Get original URL
    result4 = ta.get('/urls/' + shortcode_result)
    assert(result4.status_code == 307)
    assert(result4.data.decode('UTF-8').split('Original URL: ',1)[1] == test_url)

    # Get non-existant URL
    result5 = ta.get('/urls/' + 'ldkfjsldkfj')
    assert(result5.status_code == 404)

    # Get stats of shortcode
    result6 = ta.get('/stats/' + shortcode_result)
    assert(result6.status_code == 200)
    assert(json.loads(result6.data.decode('UTF-8'))['hits'] == str(1))

    # Increase the hit counter
    ta.get('/urls/' + shortcode_result)
    result7 = ta.get('/stats/' + shortcode_result)
    assert(json.loads(result7.data.decode('UTF-8'))['hits'] == str(2))

print("All tests passed!")
