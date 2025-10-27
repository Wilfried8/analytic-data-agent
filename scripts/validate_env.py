from app.config import load_settings

def main():
    try:
        settings = load_settings()
    except Exception as err:
        print(f"Invalide env: {err}")
        raise SystemExit(1)
    else:
        print("✅ env ok")
        print(settings)    
        
if __name__== "__main__":
    main()
