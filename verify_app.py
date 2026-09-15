from app import app

def test_routes():
    client = app.test_client()
    routes = [
        ('/', 200),
        ('/?site=CA0249', 200),
        ('/cells?tech=lte', 200),
        ('/cells?tech=gsm', 200),
        ('/cells?tech=umts', 200),
        ('/cells?tech=nr', 200),
        ('/inventory?type=boards', 200),
        ('/inventory?type=rru', 200),
        ('/import-export', 200),
        ('/api/autocomplete/sites?term=CA', 200),
        ('/api/export/site/CA0249', 200)
    ]

    all_ok = True
    for route, expected in routes:
        resp = client.get(route)
        ok = (resp.status_code == expected)
        print(f"Route {route:35} -> Code: {resp.status_code} [{'OK' if ok else 'FAILED'}]")
        if not ok:
            all_ok = False
            
    if all_ok:
        print("\n--> ALL ROUTES PASSED VERIFICATION! <--")
    else:
        print("\n--> SOME ROUTES FAILED <--")

if __name__ == "__main__":
    test_routes()
