class Metadata_Yt:

    def __init__(self, name, dict={}):
        self.name = name    # instance variable unique to each instance
        self.upload_date = dict['upload_date'],
        self.uploader =    dict['uploader'],
        self.view_count =  dict['view_count'],
        self.id =          dict['id'],
        self.format =      dict['format'],
        self.duration =    dict['duration'],
        self.title =       dict['title'],
        self.description = dict['description'],
        self.webpage_url_basename = dict['webpage_url_basename'],
        self.current_app = dict['current_app'], 
        self.download_time = dict['download_time']
