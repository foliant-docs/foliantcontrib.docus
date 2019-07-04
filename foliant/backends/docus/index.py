INDEX_HTML = '''
<!DOCTYPE HTML>
<html lang="en-US">
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=docs/{doc_id}.html">
    <script type="text/javascript">
      window.location.href = 'docs/{doc_id}.html';
    </script>
    <title>{title}</title>
  </head>
  <body>
    If you are not redirected automatically, follow this <a href="docs/{doc_id}.html">link</a>.
  </body>
</html>
'''