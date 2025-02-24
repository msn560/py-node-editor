import os
import importlib.util

LANGUAGES = {}

languages_dir = os.path.join(os.path.dirname(__file__) )

for filename in os.listdir(languages_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        lang_code = filename[:-3]  # "tr.py" -> "tr"
        file_path = os.path.join(languages_dir, filename)

        spec = importlib.util.spec_from_file_location(lang_code, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "Languages") and isinstance(module.Languages, type):
            LANGUAGES[lang_code] = module.Languages()  # Sınıfın bir örneğini oluştur