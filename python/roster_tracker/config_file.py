import os
from lxml import etree


class ConfigFile():
    def __init__(self, filename):
        self._config_filename = filename
        if not os.path.exists(self._config_filename):
            self.write_default_config()
        
        self.load()

    def write_default_config(self):
        f = open(self._config_filename, "w")
        f.write("""
<config>
    <lastLoadedDir></lastLoadedDir>
</config>
        """)
        f.close()
        
    def load(self):
        f = open(self._config_filename, "r")
        root = etree.fromstring(f.read())
        f.close()
        
        self.last_loaded_dir = root.find("lastLoadedDir").text

    def write(self):
        f = open(self._config_filename, "w")
        f.write("""
<config>
    <lastLoadedDir>%s</lastLoadedDir>
</config>
        """ % (self.last_loaded_dir if self.last_loaded_dir is not None else "", ))
        f.close()
