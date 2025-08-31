import requests
import re
from urllib.parse import urlparse, unquote_plus, parse_qs

def _get_redirect_url(maps_link: str) -> str:
    """
    Function for google consent urls and redirects
    """
    try:
        if "consent.google.com" in maps_link:
            print("URL de consentement. Extraction du lien de redirection...")
            parsed_url = urlparse(maps_link)
            query_params = parse_qs(parsed_url.query)
            
            if 'continue' in query_params:
                full_url = unquote_plus(query_params['continue'][0])
                print(f"Lien complet extrait: {full_url}")
                return full_url
        
        print(f"Résolution du lien court: {maps_link}")
        response = requests.get(maps_link, allow_redirects=True, timeout=10)
        response.raise_for_status()
        return response.url

    except Exception as e:
        print(f"Erreur: {e}")
        return ""

def extract_place_name_from_maps_link(maps_link: str) -> str:
    full_url = _get_redirect_url(maps_link)
    if not full_url:
        return ""

    try:
        match = re.search(r'/place/([^/]+)', full_url)
        
        if match:
            place_name_encoded = match.group(1)
            place_name = unquote_plus(place_name_encoded)
            place_name = place_name.replace('+', ' ')
            place_name = place_name.split('/@')[0].strip()

            return place_name
        else:
            print("Aucun nom de lieu trouvé dans l'URL.")
            return ""

    except Exception as e:
        print(f"Erreur: {e}")
        return ""

if __name__ == "__main__":
    lien_test_simple = "https://maps.app.goo.gl/euz2Y5xrzEev7CWZ6?g_st=il"

    nom = extract_place_name_from_maps_link(lien_test_simple)
    print(f"\nNom du lieu: {nom}")

