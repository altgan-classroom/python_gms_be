
def get_kisi_headers(api_key: str = None) -> dict:
    header = {'Authorization': f"KISI-LOGIN {api_key}",
              'Content-Type': 'application/json',
              'Accept': 'application/json'}
    return header