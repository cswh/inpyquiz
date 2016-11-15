"""
Usage: python inpyquiz.py

After that point your browser to http://localhost:8000.
"""
if __name__ == '__main__':
    import inpyquiz
    inpyquiz.app.debug = True
    inpyquiz.app.secret_key = 'NOTTHATSECRET'
    inpyquiz.app.run(host="0.0.0.0", port=8000)
