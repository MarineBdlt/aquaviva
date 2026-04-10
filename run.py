from booking_engine import app


if __name__ == "__main__":
    try:
        from meinheld import server
        server.listen(("0.0.0.0", 8000))
        server.run(app)
    except ImportError:
        # Fallback for environments where meinheld is unavailable.
        app.run(host="0.0.0.0", port=8000)
