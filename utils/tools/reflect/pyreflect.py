'''
python reflect method
'''
def getObj(name):
    return eval(name + '()')

def create_obj(cls_name):
    # need import class first
    cls = globals()[cls_name]
    for name in cls_name[1:]:
        cls = getattr(cls, name)

    if isinstance(cls, type):
        return cls()
    else:
        raise Exception("no such class")

def import_file(full_path_to_module):
    try:
        import os
        module_dir, module_file = os.path.split(full_path_to_module)
        module_name, module_ext = os.path.splitext(module_file)
        save_cwd = os.getcwd()
        os.chdir(module_dir)
        module_obj = __import__(module_name)
        module_obj.__file__ = full_path_to_module
        globals()[module_name] = module_obj
        os.chdir(save_cwd)
    except:
        raise ImportError

import_file('/home/somebody/somemodule.py')

sys.path.append("/home/me/mypy") 


if __name__ == "__main__":
    unittest.main(defaultTest="regressionTest")
