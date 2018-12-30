from pythonforandroid.recipes.cffi import CffiRecipe as OriginalCffiRecipe

# This workaround will be deprecated by
# https://github.com/kivy/python-for-android/pull/1545

class CffiRecipe(OriginalCffiRecipe):
    # We override this recipe to allow for python3
    depends = ['python3', 'libffi', 'setuptools']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['CFLAGS'] += ' -I' + self.ctx.python_recipe.include_root(arch.arch)
        env['LDFLAGS'] += ' -L' + self.ctx.python_recipe.link_root(arch.arch)
        env['LDFLAGS'] += " -lpython3"
        return env


recipe = CffiRecipe()
