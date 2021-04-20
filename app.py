from app import app, socketio

if __name__ == "__main__":
  print("Flask app running at http://0.0.0.0:5000")
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  socketio.run(app, host="localhost", port=5000)
