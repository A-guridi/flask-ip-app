import os
from __init__ import create_app

if __name__ == '__main__':
    # simple main function to run the app on a docker file
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
