SONGS = "songs"
PHOTO = "photos"
MUSIC = "music"
IMAGES = "images"


SUPPORTED_FILE_TYPES = {
    MUSIC: {
        'audio/mpeg': 'mp3'
    },
    IMAGES: {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'application/pdf': 'pdf',
    }
}


KB = 1024
MB = 1024 * KB

# размеры файлов для каждого типа
DEFAULT_MAX_SIZE = 1 * MB  # 1 MB для большинства типов
MP3_MAX_SIZE = 20 * MB  # 20 MB для MP3


MAX_FILE_SIZES = {
    'mp3': MP3_MAX_SIZE,
    'jpg': DEFAULT_MAX_SIZE,
    'png': DEFAULT_MAX_SIZE,
    'pdf': DEFAULT_MAX_SIZE,
}

