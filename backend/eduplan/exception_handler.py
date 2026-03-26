from rest_framework.views import exception_handler
from rest_framework.response import Response


def _stringify_errors(data):
    if isinstance(data, dict):
        parts = []
        for field, messages in data.items():
            if isinstance(messages, (list, tuple)) and messages:
                parts.append(f"{field}: {messages[0]}")
            else:
                parts.append(f"{field}: {messages}")
        return '; '.join(parts)
    if isinstance(data, (list, tuple)) and data:
        return str(data[0])
    return str(data)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response({'error': 'Internal server error'}, status=500)

    if isinstance(response.data, dict) and 'detail' in response.data:
        message = response.data['detail']
    else:
        message = _stringify_errors(response.data)

    response.data = {'error': str(message)}
    return response
