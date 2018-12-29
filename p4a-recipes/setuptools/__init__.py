from pythonforandroid.recipe import PythonRecipe

# We need to override the recipe for setuptools to modify its dependencies: we
# use python3 and not python3crystax.

class SetuptoolsRecipe(PythonRecipe):
    version = '40.0.0'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.zip'

    depends = ['python3']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
