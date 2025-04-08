"""
Sample HTML content for testing the crawler functions.
"""

# Simple HTML page with title and content
SIMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page Title</title>
</head>
<body>
    <h1>Test Page Heading</h1>
    <p>This is a test paragraph with some content.</p>
    <p>This is another paragraph with more content.</p>
</body>
</html>
"""

# HTML page with links (internal and external)
HTML_WITH_LINKS = """
<!DOCTYPE html>
<html>
<head>
    <title>Page With Links</title>
</head>
<body>
    <h1>Page With Links</h1>
    <nav>
        <ul>
            <li><a href="https://sites.google.com/view/metropoleballard/home">Home</a></li>
            <li><a href="https://sites.google.com/view/metropoleballard/about">About</a></li>
            <li><a href="https://sites.google.com/view/metropoleballard/contact">Contact</a></li>
            <li><a href="https://external-site.com">External Link</a></li>
            <li><a href="/view/metropoleballard/resources">Resources (Relative)</a></li>
            <li><a href="javascript:void(0)">JavaScript Link</a></li>
            <li><a href="#">Anchor Link</a></li>
            <li><a href="mailto:info@example.com">Email Link</a></li>
        </ul>
    </nav>
    <p>This is a page with various types of links.</p>
</body>
</html>
"""

# HTML page with no title tag, only h1
HTML_NO_TITLE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Page Heading Only</h1>
    <p>This page has no title tag, only an h1 heading.</p>
</body>
</html>
"""

# HTML page with navigation, footer, and other elements to be removed
HTML_WITH_ELEMENTS_TO_REMOVE = """
<!DOCTYPE html>
<html>
<head>
    <title>Page With Elements To Remove</title>
</head>
<body>
    <header>This is a header that should be removed</header>
    <nav>This is navigation that should be removed</nav>
    <div class="content">
        <h1>Main Content</h1>
        <p>This is the main content that should be kept.</p>
    </div>
    <footer>This is a footer that should be removed</footer>
    <div class="sidebar">This is a sidebar that should be removed</div>
</body>
</html>
"""

# HTML page with boilerplate text to be cleaned
HTML_WITH_BOILERPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Page With Boilerplate</title>
</head>
<body>
    <h1>Page With Boilerplate</h1>
    <p>This is the main content.</p>
    <p>Back to Top | Back to Home</p>
    <p>Metropole HOA | Metropole Ballard</p>
    <p>Copyright | All Rights Reserved</p>
    <p>Privacy Policy | Terms of Service</p>
    <p>Contact Us | Sign In | Sign Out</p>
</body>
</html>
"""

# HTML page with circular references
HTML_CIRCULAR_REF_1 = """
<!DOCTYPE html>
<html>
<head>
    <title>Page 1 (Circular)</title>
</head>
<body>
    <h1>Page 1</h1>
    <p>This page links to Page 2, which links back to Page 1.</p>
    <a href="https://sites.google.com/view/metropoleballard/page2">Go to Page 2</a>
</body>
</html>
"""

HTML_CIRCULAR_REF_2 = """
<!DOCTYPE html>
<html>
<head>
    <title>Page 2 (Circular)</title>
</head>
<body>
    <h1>Page 2</h1>
    <p>This page links back to Page 1, creating a circular reference.</p>
    <a href="https://sites.google.com/view/metropoleballard/page1">Go to Page 1</a>
</body>
</html>
"""
