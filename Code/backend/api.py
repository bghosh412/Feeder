import ujson
import services
from microdot import Microdot, Response, send_file

app = Microdot()

@app.after_request
def enable_cors(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/api/ping', methods=['GET'])
def ping(request):
    return ujson.dumps({'status': 'ok'})

@app.route('/api/ping', methods=['OPTIONS'])
def ping_options(request):
    return ''

@app.route('/api/schedule', methods=['GET'])
def get_schedule(request):
    data = services.read_schedule()
    if data:
        return ujson.dumps(data)
    return Response(ujson.dumps({'error': 'Could not read schedule'}), status=500)

@app.route('/api/schedule', methods=['POST'])
def set_schedule(request):
    try:
        print("Received POST request to /api/schedule")
        print("Request body:", request.body)
        schedule_data = request.json
        print("Parsed JSON:", schedule_data)
        success = services.write_schedule(schedule_data)
        print("Write result:", success)
        if success:
            return ujson.dumps({'status': 'ok'})
        else:
            return Response(ujson.dumps({'error': 'Write failed'}), status=500)
    except Exception as e:
        print("Error in set_schedule:", str(e))
        return Response(ujson.dumps({'error': str(e)}), status=400)

@app.route('/api/schedule', methods=['OPTIONS'])
def schedule_options(request):
    return ''

@app.route('/', methods=['GET'])
def index(request):
    return send_file('../frontend/index.html')

@app.route('/<path:path>', methods=['GET'])
def static_files(request, path):
    try:
        return send_file(f'../frontend/{path}')
    except:
        return Response('Not found', status=404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
