import ujson
import services
from microdot import Microdot, Response

app = Microdot()
Response.default_content_type = 'application/json'

@app.after_request
def enable_cors(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/ping', methods=['GET'])
def ping(request):
    return ujson.dumps({'status': 'ok'})

@app.route('/api/schedule', methods=['GET'])
def get_schedule(request):
    data = services.read_schedule()
    if data:
        return ujson.dumps(data)
    return Response(ujson.dumps({'error': 'Could not read schedule'}), status=500)

@app.route('/api/schedule', methods=['POST'])
def set_schedule(request):
    try:
        schedule_data = request.json
        success = services.write_schedule(schedule_data)
        if success:
            return ujson.dumps({'status': 'ok'})
        else:
            return Response(ujson.dumps({'error': 'Write failed'}), status=500)
    except Exception as e:
        return Response(ujson.dumps({'error': str(e)}), status=400)

if __name__ == '__main__':
    app.run(debug=True)
