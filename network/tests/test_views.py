from django.test import SimpleTestCase, Client, TestCase
from django.urls import reverse, resolve
from blog.views import blog_index, blog_detail, blog_category

class TestUrlResponseCodes(TestCase):
    """This set of tests uses Django TestCase as described
     in https://docs.djangoproject.com/en/3.0/topics/testing/tools/
     The tests also use previously prepared test data.
     They uses a simple client to test the return codes from projects/urls.py
     using a variety of inputs.
     """

    # Load blog test data previously dumped from database.
    fixtures = ['blog.json']

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    # Start with /blog_index/.

    def test_network_index_is_returned(self):
        """Requires a path of '/blog/'."""
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200) #(actual, expected)

    def test_blog_index_not_found_error(self):
        """Requires a path of '/blog/' so let's drop leading '/'."""
        response = self.client.get('blog/')
        self.assertEqual(response.status_code, 404) #(actual, expected)

    def test_blog_index_perm_redirected(self):
        """Requires a path of '/blog/' so let's drop trailing '/'."""
        response = self.client.get('/blog')
        self.assertEqual(response.status_code, 301) #(actual, expected)

    # Now test /blog/<int>
    def test_blog_detail_is_returned(self):
        """Requires a <int:pk> to be passed, so let's create one and pass it."""
        response = self.client.get('/blog/post/1')
        self.assertEqual(response.status_code, 200) #(actual, expected)

    def test_blog_detail_is_not_returned_if_char(self):
        """Requires a <int:pk> to be passed, so let's pass a char."""
        response = self.client.get('/blog/a')
        self.assertEqual(response.status_code, 404) #(actual, expected)

    def test_blog_detail_is_not_found_error(self):
        """Requires a <int:pk> to be passed, so let's pass a long int."""
        response = self.client.get('/blog/99999999999999')
        self.assertEqual(response.status_code, 404) #(actual, expected)

    def test_blog_detail_is_not_found_message(self):
        """Requires a <int:pk> to be passed, so let's pass a long int."""
        response = self.client.get('/blog/post/99999999999999')
        self.assertEqual(response.content, b'Post does not exist.') #(actual, expected)

    # Now test /blog/<category>
    def test_blog_category_is_returned(self):
        """Requires a <category> to be passed, so let's pass one."""
        response = self.client.get('/blog/category/Test category 1')
        self.assertEqual(response.status_code, 200) #(actual, expected)

    def test_blog_category_is_not_returned_if_int(self):
        """Requires a <category> to be passed, so let's pass an int."""
        response = self.client.get('/blog/category/1')
        self.assertEqual(response.status_code, 404) #(actual, expected)

    def test_blog_category_is_not_found_error(self):
        """Requires a <category> to be passed, so let's pass a random string."""
        response = self.client.get('/blog/category/abcdefg')
        self.assertEqual(response.status_code, 404) #(actual, expected)

    def test_blog_category_is_not_found_message(self):
        """Requires a <category> to be passed, so let's pass a random string."""
        response = self.client.get('/blog/category/abcdefg')
        self.assertEqual(response.content, b'Category does not exist.') #(actual, expected)

class TestUrlsToViewsMapping(SimpleTestCase):
    """Test to ensure the urls return the correct (<namespace>:<url_name>) mapping to views.
    """
    def test_blog_index_is_resolved(self):
        """Test blog_index."""
        url = reverse('blog:blog_index')
        self.assertEqual(resolve(url).func, blog_index) #(actual, expected)

    def test_blog_detail_is_resolved(self):
        """Test blog_detail - requires a <int:pk> to be passed."""
        url = reverse('blog:blog_detail', args=[1])
        self.assertEqual(resolve(url).func, blog_detail) #(actual, expected)

    def test_blog_category_is_resolved(self):
        """ Test blog_category - requires a <category> to be passed."""
        url = reverse('blog:blog_category', args=['Test category 1'])
        self.assertEqual(resolve(url).func, blog_category) #(actual, expected)
