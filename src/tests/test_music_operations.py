from conftest import client
import logging

file = {'photo_file': ('doberman1.jpg', open(r"D:\Projects\s3-training\doberman1.jpg", 'rb'))}
file_name = None


def test_create_album(login_user):
    logging.info("TOKEN BEFORE SENDING TO ENDPOINT: %s", login_user['access_token'])
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.post(
        url="/album/",
        headers=headers,
        data={"name": "album_name"},
        files=file
    )
    assert response.status_code == 201
    assert "photo_filename" in response.json()
    global file_name
    file_name = response.json()['photo_filename'].split("/")[-1]
    logging.info('Photo file name: %s', file_name)
    logging.info("Test 'create_album' was successful")


def test_get_list_albums(login_user):
    fields = ["name", "artist_id", "photo_url", "id", "artist", "songs", "created_at", "updated_at"]
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.get(
        url="/album/",
        headers=headers,
        # json={"name": "album_name"},
    )
    assert response.status_code == 200
    response_json = response.json()[0]
    # print(response_json)
    assert all(field in response_json for field in fields)
    assert response_json["name"] == 'album_name'
    assert response_json["id"] == 1
    assert response_json['artist_id'] == 1
    assert response_json['artist']['username'] == 'staiddd'
    assert response_json['artist']['email'] == 'user@example.com'
    assert response_json['photo_url'].split("/")[-1] == file_name

    logging.info("Test 'get_list_albums' was successful")


def test_update_album(login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.patch(
        url="/album/1/",
        headers=headers,
        data={"name": "album_name1"},
        files=file
    )
    assert response.status_code == 200
    assert "photo_filename" in response.json()
    
    global file_name
    logging.info('Photo file name after update:  %s', response.json()['photo_filename'])
    logging.info('GLOBAL Photo file name: %s', file_name)
    file_name = response.json()['photo_filename'].split("/")[-1]
    logging.info('GLOBAL Photo file name after UPDATE: %s', file_name)

    logging.info("Test 'update_album' was successful")


def test_download_album_photo():
    response = client.get(
        url="/album/download/",
        params={"file_name": file_name}
    )
    assert response.status_code == 200
    assert response.headers['Content-Disposition'] == f'attachment;filename={file_name}'
    assert response.headers['Content-Type'] == 'application/octet-stream'

    logging.info("Test 'download_album_photo' was successful")


files = {
    'photo_file': ('doberman2.jpg', open(r"D:\Projects\s3-training\doberman1.jpg", 'rb')),
    'song_file': ('song.mp3', open(r"D:\Projects\s3-training\song.mp3", 'rb'))
}

song_filename = None
photo_filename = None


def test_create_song(login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.post(
        url="/music/",
        headers=headers,
        data={
            "name": "song_name",
            "genre": "rock",
            "album_id": 1,
        },
        files=files
    )
    assert response.status_code == 201
    assert "song_filename" and "photo_filename" in response.json()

    global song_filename, photo_filename, file_name

    logging.info("Song file name after creating song before updating: %s", song_filename)
    logging.info("Photo file name after creating song before updating: %s", photo_filename)
    
    assert song_filename == photo_filename == None

    song_filename = response.json()["song_filename"].split("/")[-1]
    photo_filename = response.json()["photo_filename"].split("/")[-1]
    
    assert song_filename != photo_filename != None

    logging.info("Song file name after creating song after updating: %s", song_filename)
    logging.info("Photo file name after creating song after updating: %s", photo_filename)

    logging.info("Test 'test_create_song' was successful")


def test_get_all_songs(login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.get(
        url="/music/",
        headers=headers
    )
    assert response.status_code == 200
    response_json = response.json()[0]
    global song_filename, photo_filename
    assert response_json["id"] == 1
    assert response_json["name"] == "song_name"
    assert response_json["artist_id"] == 1
    assert response_json["album_id"] == 1
    assert response_json["file_url"].split("/")[-1] == song_filename
    assert response_json["photo_url"].split("/")[-1] == photo_filename
    assert response_json["artist"]["username"] == "staiddd"
    assert response_json["artist"]["email"] == "user@example.com"
    assert response_json["album"]["name"] == "album_name1"
    assert response_json["album"]["artist_id"] == 1
    assert response_json["album"]["photo_url"].split("/")[-1] == file_name

    logging.info("Song file name after getting songs: %s", song_filename)
    logging.info("Photo file name after getting songs: %s", photo_filename)

    logging.info("Test 'get_all_songs' was successful")


def test_update_song(login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.patch(
        url="/music/1/",
        headers=headers,
        data={
            "name": "song_name1",
            "genre": "pop"
        },
        files=files
    )
    assert response.status_code == 200

    global song_filename, photo_filename

    logging.info("Song file name after updating song before updating: %s", song_filename)
    logging.info("Photo file name after updating song before updating: %s", photo_filename)
    
    assert song_filename != photo_filename != None

    song_filename = response.json()["song_filename"].split("/")[-1]
    photo_filename = response.json()["photo_filename"].split("/")[-1]

    logging.info("Song file name after updating song after updating: %s", song_filename)
    logging.info("Photo file name after updating song after updating: %s", photo_filename)

    logging.info("Test 'update_song' was successful")


def test_delete_song(login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.delete(
        url="/music/1/",
        headers=headers
    )
    assert response.status_code == 204

    global song_filename, photo_filename

    assert song_filename != photo_filename != None

    logging.info("Song file name after deleting song before updating: %s", song_filename)
    logging.info("Photo file name after deleting song before updating: %s", photo_filename)

    song_filename = photo_filename = None

    logging.info("Song file name after deleting song after updating: %s", song_filename)
    logging.info("Photo file name after deleting song after updating: %s", photo_filename)

    logging.info("Test 'delete_song' was successful")


def test_delete_album(login_user):
    headers = {"Authorization": f"Bearer {login_user['access_token']}"}
    response = client.delete(
        url="/album/1/",
        headers=headers
    )
    global file_name
    logging.info('GLOBAL DELETED Photo file name: %s', file_name)
    assert response.status_code == 204
    file_name = None
    logging.info('GLOBAL Photo file name after tests: %s', file_name)

    logging.info("Test 'delete_album' was successful")