from pythonforandroid.recipe import PythonRecipe


class KociembaRecipe(PythonRecipe):
    version = '1.2'
    url = 'https://github.com/muodov/kociemba/archive/{version}.tar.gz'
    depends = ['python3', 'setuptools', 'cffi', 'libffi']

    call_hostpython_via_targetpython = False


recipe = KociembaRecipe()
