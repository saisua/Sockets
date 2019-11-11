from os import listdir
__all__ = [directory[:-3] for directory in listdir(__file__[:-11]) if directory[-3:] == '.py']