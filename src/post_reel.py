import time
import requests
import os

# domain = "http://127.0.0.1:8000"
domain = "https://lesecteur.fr"

def upload_video(video_path):
    headers = {
        "User-Agent":"LeSecteur.fr Reel API"
    }
    files = {
        "video": open(video_path, "rb")
    }
    req = requests.post(f"{domain}/webhook/reel/upload", headers=headers, files=files)
    print(req.status_code, req.text)
    if req.status_code == 200:
        return req.text
    return None


def delete_video():
    headers = {
        "User-Agent":"LeSecteur.fr Reel API"
    }
    req = requests.post(f"{domain}/webhook/reel/delete", headers=headers)
    print(req.status_code, req.text)

def post(video_file_path):
    # Remplacez ces valeurs par les vôtres
    page_id = "195919896943493"
    access_token = "EAAMu32QWEroBOxzOBs9vj8q2sSbsi7iH4C6XT020fenEHGkGugK2G6U46OKLZBtEti3iqzsfd27oewXxJbmdZBEGQEuwj22WFTrCO8Co8B5DORSFgxLwx9tCZBOl5Mhra1bipp8Vktb949aV2KhYWjvv8uYDzh0S4bL0yKhr81AkYk75Fl1XzJ5a107BDX4eff75iBnMZCsbVVLBjjkkbnsZD"

    # URL de la requête
    url = f"https://graph.facebook.com/v18.0/{page_id}/video_reels"

    # En-têtes de la requête
    headers = {
        "Content-Type": "application/json"
    }

    # Données de la requête
    data = {
        "upload_phase": "start",
        "access_token": access_token
    }

    # Exécution de la requête POST
    response = requests.post(url, headers=headers, json=data)

    # Affichage de la réponse
    print(response.json())


    video_id = response.json()["video_id"]
    file_size = str(os.path.getsize(video_file_path))


    # URL de la requête
    url = f"https://rupload.facebook.com/video-upload/v18.0/{video_id}"

    # En-têtes de la requête
    headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": file_size
    }

    # Lecture des données binaires à partir du fichier vidéo
    with open(video_file_path, "rb") as file:
        file_data = file.read()

    # Exécution de la requête POST avec les données binaires
    response = requests.post(url, headers=headers, data=file_data)

    # Affichage de la réponse
    print(response.json())


    description = "Nos trouvailles Amazon du jour #amazonfinds #amazon"

    # URL de la requête
    url = f"https://graph.facebook.com/v18.0/{page_id}/video_reels"

    # Paramètres de la requête
    params = {
        "access_token": access_token,
        "video_id": video_id,
        "upload_phase": "finish",
        "video_state": "PUBLISHED",
        "description": description
    }

    # Exécution de la requête POST
    response = requests.post(url, params=params)

    # Affichage de la réponse
    print(response.json())

def post_insta(video_url):
    # Remplacez ces valeurs par les vôtres
    # Get it by this endpoint : "{fb_page_id}?fields=instagram_business_account&access_token="
    ig_business_id = "17841460669225957"
    access_token = "EAAMu32QWEroBO7NZCkTRnSWSWK83E2J6UrfQEuGI7qlKIcJ43EMvFzAZBzBH9ReLZAnB2rRFOZBizRpGrlHwg1VEWo6L8NduNlsNbG3XVpa0J7keDpy4UcboIuKVTHK2VKy4ueBku9xnmp5oIBw5XPm0qbbfYxHch4jc99iQZCYwo4Lx5R7v8e5x48HZAO7LbZAJ6Xsd1AAlivyF9x6a57kDMwZD"

    caption = "Les trouvailles Amazon du jour que tout le monde s'arrache #amazonfinds #amazon"


    # URL de la requête
    url = f"https://graph.facebook.com/v18.0/{ig_business_id}/media"

    # Données de la requête
    data = {
        "media_type":"REELS",
        "caption":caption,
        "video_url":video_url,
        "share_to_feed":True,
        "access_token": access_token
    }

    # Exécution de la requête POST
    response = requests.post(url, json=data)

    # Affichage de la réponse
    print(response.status_code,response.json())


    video_id = response.json()["id"]

    # URL de la requête
    url = f"https://graph.facebook.com/v18.0/{ig_business_id}/media_publish"

    params = {
        "creation_id": video_id,
        "access_token": access_token
    }

    # Exécution de la requête POST avec les données binaires
    response = requests.post(url, params=params)

    # Affichage de la réponse
    print(response.status_code,response.json())
    while response.status_code!=200:
        time.sleep(20)
        response = requests.post(url, params=params)
        print(response.status_code,response.json())

# delete_video()
# upload_video(r"innovgadgetspot_1\output.mov_clip_1704997350cps_.mp4")
# post_insta(r"innovgadgetspot_1\output.mp4")
# post(r"innovgadgetspot_1\output.mp4")